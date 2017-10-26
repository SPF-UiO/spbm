import datetime
import os.path
import time
from decimal import Decimal

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.db import transaction
from django.db.models import Max
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.formats import localize
from django.utils.translation import ugettext as _
from django.views.generic import TemplateView

from spbm.helpers.decorators import permission_required
from spbm.helpers.f60 import f60
from ..models import Society, Event, Invoice

# TODO Generalize? Import? Something?
messages.DEFAULT_TAGS.update({messages.ERROR: 'danger'})


def unix_time(dt) -> int:
    """
    Returns unix time (epoch) based on given datetime.

    :param dt: datetime object.
    :return: UNIX time.
    """
    return int(time.mktime(dt.timetuple()))


class InvoicingView(LoginRequiredMixin, TemplateView):
    """
    View for treating invoice overview and processing!
    """

    template_name = "invoices/index.jinja"

    def get_context_data(self, **kwargs):
        last_period = Invoice.objects.last().period
        today = datetime.date.today()
        next_period = datetime.date(last_period.year, last_period.month,
                                    settings.SPBM['dates']['invoicing']) + relativedelta(months=1)
        # Fixes the no events in period problem
        if ((Event.objects.filter(processed__isnull=True).count()) == False):
            while next_period < today:
                next_period += relativedelta(months=1)

        if last_period.month == today.month:
            warning = _("You <strong>should not</strong> close a period twice in a month without good reason!")
        else:
            warning = None

        return {
            'progress': (today - last_period) / (next_period - last_period),
            'days_left': next_period - today,
            'warning': warning,
            'unprocessed_events': Event.objects.filter(processed__isnull=True).count(),
            'unpaid_invoices': Invoice.objects.filter(paid=False),
            'all_invoices': Invoice.objects.all(),
        }

    @transaction.atomic
    def post(self, request):
        if request.POST['action'] == "close_period":
            return self.close_period(request)
        elif request.POST['action'] == 'mark_paid':
            return self.mark_as_paid(request, request.POST.get('inv_id'))

    @method_decorator(permission_required(
        perm='society.close_period', raise_exception=True,
        message=_("You do not have the required permission to close billing periods.")))
    def close_period(self, request):
        """
        Closes the current invoicing period.

        Note that the period cannot be closed twice on the same day, *unless* a new invoice for a previously not
        invoiced society is available.
        """
        events = Event.objects.filter(processed__isnull=True)
        societies = events.values('society').distinct()
        period_date = timezone.now()
        try:
            for society in societies:
                society = Society.objects.get(id=society['society'])
                invoice_number = Invoice.objects.all().aggregate(Max('invoice_number')).get('invoice_number__max')
                if invoice_number is None:
                    invoice_number = 1
                else:
                    invoice_number += 1

                period_invoice = Invoice(
                    society=society,
                    invoice_number=invoice_number,
                    period=period_date,
                    created_by=request.user,
                )
                # We try to save the invoice, which might fail due to a UNIQUE constraint
                # This is where our try/catch helps. Alternatively...
                # TODO Filter and see if we can close or not, rather than catching an IntegrityError
                period_invoice.save()
                for event in events.filter(society=society):
                    event.invoice = period_invoice
                    event.processed = period_date
                    event.save()

            messages.add_message(
                request, messages.SUCCESS, _("You have successfully closed the invoicing period."))
        # If it was the unique constraint, let's show an error message
        except IntegrityError:
            messages.add_message(request, messages.ERROR, _("You cannot close a period twice in a day!"))

        return redirect(reverse('invoices'))

    @method_decorator(permission_required(
        'society.mark_paid', raise_exception=True,
        message=_("You do not have the required permission to mark invoices as paid.")))
    def mark_as_paid(self, request, invoice_id):
        """
        Marks an invoice as paid.
        """
        invoice = Invoice.objects.get(id=invoice_id)
        invoice.paid = True
        invoice.save()
        messages.add_message(request, messages.SUCCESS,
                             _("You've successfully marked {invoice} as paid.".format(invoice=invoice)))
        return redirect(reverse('invoices'))


@login_required
def view_invoice(request, society_name, date):
    """
    Displays an invoice.
    :param request:
    :param society_name: The society name for which the invoice will be queried.
    :param date: The date for the invoice.
    :return:
    """
    society = get_object_or_404(Society, shortname=society_name)
    invoice = get_object_or_404(Invoice, society=society, period=date)
    events = Event.objects.filter(society=society, processed=date)

    event_total = invoice.get_total_event_cost()
    invoice_sum = invoice.get_total_cost()
    spf_fee = invoice_sum - event_total

    items = []

    # Go through all the events
    for event in events:
        event_hours = event.hours
        event_cost = event.cost
        items.append({
            'description': "{date}: {title}".format(date=event.date, title=event.name),
            'count': event_hours,
            'item_cost': (event_cost / event_hours).quantize(Decimal('.01')),
            'line_cost': event_cost,
        })

    # Add the SPF fee at the end
    items.append({
        'description': _("SPF fee: {percent}% of {event_cost}".format(percent=30, event_cost=localize(event_total))),
        'item_cost': spf_fee,
        'line_cost': spf_fee,
    })

    return render(request, "invoices/view.jinja", {
        'items': items,
        'cost': {
            'total': invoice_sum,
            'events': event_total,
            'fee': spf_fee,
        },
        'invoice': invoice,
    })


@login_required
def generate_pdf(request, society_name: str, date: str):
    """
    Generate a PDF for the given society and invoice/period date.

    :param request:
    :param society_name: Short name for the society.
    :param date: The date for which we'll look up the invoice and its events.
    :return:
    """
    society = get_object_or_404(Society, shortname=society_name)
    invoice = get_object_or_404(Invoice, society=society, period=date)
    events = Event.objects.filter(society=society, processed=date)

    filename = os.path.join("static_invoice", society.shortname + "-" + str(date) + ".pdf")

    # If the PDF already exists, let's fetch it
    if os.path.isfile(filename):
        return HttpResponse(open(filename, "rb"), content_type="application/pdf")

    pdf_invoice = f60(filename, overskriv=True)
    pdf_invoice.settKundeinfo(1, society.name)
    pdf_invoice.settFakturainfo(
        fakturanr=1,
        utstedtEpoch=unix_time(events[0].processed),
        forfallEpoch=unix_time(events[0].processed) + 3600 * 24 * 7,
        fakturatekst="Faktura fra SPF for utlån.\nFaktura nr " + str(invoice.invoice_number))
    pdf_invoice.settFirmainfo(
        {
            'firmanavn': "Studentkjellernes Personalforening",
            'kontaktperson': '',
            'kontonummer': 60940568407,
            'organisasjonsnummer': 890747272,
            'adresse': 'Problemveien 13,\nv/ Bunnpris Blindern, Postboks 71',
            'postnummer': 0o0313,
            'poststed': 'Oslo',
            'telefon': '',
            'epost': 'spf-styret@studorg.uio.no'
        })

    linjer = []
    totcost = 0
    for e in events:
        hours = e.get_hours()
        cost = e.get_cost()
        avg_hourly = cost / hours
        linjer.append(["" + str(e.date) + ": " + e.name, hours, avg_hourly, 0])
        totcost += cost

    totcost = totcost.quantize(Decimal(10) ** -2)
    spf_fee = totcost * Decimal("0.30")
    linjer.append(["SPF-avgift: " + str(totcost) + "*0.3", 1, spf_fee, 0])

    pdf_invoice.settOrdrelinje(linjer)
    pdf_invoice.lagEpost()

    return HttpResponse(open(filename, "rb"), content_type="application/pdf")
