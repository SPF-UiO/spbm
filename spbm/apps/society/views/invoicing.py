import datetime
import os.path
import time
from decimal import Decimal

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError, models
from django.db import transaction
from django.db.models import Max, Count, Sum, Avg, F, Value, ExpressionWrapper
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.formats import localize
from django.utils.translation import ugettext as _
from django.views.generic import TemplateView

from spbm.helpers.decorators import permission_required
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
        if not (Event.objects.filter(processed__isnull=True).count()):
            while next_period < today:
                next_period += relativedelta(months=1)

        if last_period.month == today.month:
            warning = _("You <strong>should not</strong> close a period twice in a month without good reason!")
        else:
            warning = None

        # Uses SUM over each invoices series of shifts hours and shift wages
        invoices_with_cost_annotation = Invoice.objects.all().annotate(
            event_cost=Sum(F('events__shifts__hours') * F('events__shifts__wage'),
                           output_field=models.DecimalField(decimal_places=2))).annotate(
            total_cost=ExpressionWrapper(F('event_cost') + (F('event_cost') * settings.SPBM.get('fee')),
                                         output_field=models.DecimalField(decimal_places=2))).select_related()

        unpaid_invoices_with_cost_annotation = invoices_with_cost_annotation.filter(paid=False)

        return {
            'progress': (today - last_period) / (next_period - last_period),
            'days_left': next_period - today,
            'warning': warning,
            'unprocessed_events': Event.objects.filter(processed__isnull=True).count(),
            'unpaid_invoices': unpaid_invoices_with_cost_annotation,
            'all_invoices': invoices_with_cost_annotation,
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
    invoice = get_object_or_404(Invoice.objects.select_related(), society__shortname=society_name, period=date)
    events = Event.objects.filter(society__shortname=society_name, processed=date)

    invoice_event_only_sum = invoice.get_total_event_cost()
    invoice_with_fee_sum = invoice.get_total_cost()
    spf_fee = invoice_with_fee_sum - invoice_event_only_sum

    items = []

    # Go through all the events
    for event in events:
        items.append({
            'description': "{date}: {title}".format(date=event.date, title=event.name),
            'count': event.sum_hours,
            'item_cost': (event.sum_costs / event.sum_hours).quantize(Decimal('.01')),
            'line_cost': event.sum_costs.quantize(Decimal('.01')),
        })

    # Add the SPF fee at the end
    items.append({
        'item_cost': spf_fee,
        'line_cost': spf_fee,
        'description': _(
            "SPF fee: {percent:.1%} of NOK {event_cost}".format(percent=settings.SPBM.get('fee'),
                                                                event_cost=localize(invoice_event_only_sum))),
    })

    return render(request, "invoices/view.jinja", {
        'items': items,
        'cost': {
            'total': invoice_with_fee_sum,
            'events': invoice_event_only_sum,
            'fee': spf_fee,
        },
        'invoice': invoice,
    })


@login_required
def generate_pdf(request, society_name: str, date: str):  # pragma: no cover
    """
    Generate a PDF for the given society and invoice/period date.

    This was removed 17th of June 2018, as it had for a longer period no longer been necessary either way,
    as invoices were sent using other applications and systems, especially for following up.

    This remains here as a note to history, to the messy code before this commit, and as a stub for the day in the
    future where an API will do this for us.

    For the sake of history, our f60.py was from:
        https://sourceforge.net/p/finfaktura/code/ci/master/tree/finfaktura/f60.py.
    (I can't believe it has actually been updated.)

    An alternative implementation seems to be interesting too, although less updated, from 2014:
        https://github.com/torbjo/f60-giro/tree/master/f60

    :param request:
    :param society_name: Short name for the society.
    :param date: The date for which we'll look up the invoice and its events.
    :return:
    """
    raise NotImplementedError
