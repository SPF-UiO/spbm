import time
from decimal import Decimal

import os.path
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Max
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.utils.formats import localize
from django.utils.translation import ugettext as _

from helpers.auth import user_allowed_society
from helpers.f60 import f60
from ..models import Society, Event, Invoice


@login_required
def redirect_society(request):
    return redirect(index, society_name=request.user.spfuser.society.shortname)


@login_required
def index(request, society_name):
    society = get_object_or_404(Society, shortname=society_name)
    if not user_allowed_society(request.user, society):
        return render(request, "errors/unauthorized.jinja")

    events = Event.objects.filter(society=society)
    proc_vals = events.values('processed').distinct().exclude(processed__isnull=True).order_by('-processed')
    invoices = Invoice.objects.filter(society=society).order_by('-period')

    return render(request, "invoices/index.jinja",
                  {'proc_vals': proc_vals, 'cur_page': 'invoices', 'invoices': invoices})


def unix_time(dt) -> int:
    """
    Returns unix time (epoch) based on given datetime.

    :param dt: datetime object.
    :return: UNIX time.
    """
    return int(time.mktime(dt.timetuple()))


@login_required
def view_invoice(request, society_name, date):
    society = get_object_or_404(Society, shortname=society_name)
    invoice = get_object_or_404(Invoice, society=society, period=date)
    events = Event.objects.filter(society=society, processed=date)

    event_total = invoice.get_total_event_cost()
    invoice_sum = invoice.get_total_cost()
    spf_fee = invoice_sum - event_total

    items = []

    # Go through all the events
    for event in events:
        event_hours = event.get_hours()
        event_cost = event.get_cost()
        items.append({
            'description': "{date}: {title}".format(date=event.date, title=event.name),
            'count': event_hours,
            'item_cost': event_cost / event_hours,
            'line_cost': event_cost,
        })

    # Add the SPF fee at the end
    items.append({
        'description': _("SPF fee: {percent}% of {event_cost}".format(percent=30, event_cost=localize(event_total))),
        'item_cost': spf_fee,
    })

    return render(request, "invoices/view.jinja",
                  {'items': items,
                   'cost': {
                       'total': invoice_sum,
                       'events': event_total,
                       'fee': spf_fee
                   },
                   'date': date,
                   'society': society_name
                   })


@login_required
def generate_pdf(request, society_name: str, date: str):
    """
    Generate a PDF for the given society and invoice/period date.

    :param request:
    :param society_name: Short name for the society.
    :param date:
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
        linjer.append(["" + str(e.date) + ": " + e.name, 1, e.get_cost(), 0])
        totcost += e.get_cost()

    totcost = totcost.quantize(Decimal(10) ** -2)
    spf_fee = totcost * Decimal("0.30")
    linjer.append(["SPF-avgift: " + str(totcost) + "*0.3", 1, spf_fee, 0])

    pdf_invoice.settOrdrelinje(linjer)
    pdf_invoice.lagEpost()

    return HttpResponse(open(filename, "rb"), content_type="application/pdf")


@login_required
def invoices_list(request):
    invoices = Invoice.objects.all().order_by('-invoice_number')
    return render(request, "invoices/list.jinja", {'invoices': invoices})


@login_required
@transaction.atomic
def invoices_all(request):
    if request.method == "POST":
        if request.POST.get('action') == "close_period":
            if not request.user.has_perm("society.close_period"):
                raise PermissionDenied()

            events = Event.objects.filter(processed__isnull=True)
            societies = events.values('society').distinct()
            period = timezone.now()
            for soc in societies:
                soc = Society.objects.get(id=soc['society'])
                print("Society=" + str(soc))
                invoice_number = Invoice.objects.all().aggregate(Max('invoice_number')).get('invoice_number__max')
                print("InvNo=" + str(invoice_number))
                if invoice_number is None:
                    invoice_number = 1
                else:
                    invoice_number += 1

                inv = Invoice(
                    society=soc,
                    invoice_number=invoice_number,
                    period=period
                )
                inv.save()
                for event in events.filter(society=soc):
                    print("->Event: " + str(event))
                    event.invoice = inv
                    event.processed = period
                    event.save()
            return redirect(invoices_all)
        elif request.POST.get('action') == 'mark_paid':
            if not request.user.has_perm('society.mark_paid'):
                raise PermissionDenied(_("You do not have the permission to mark invoices as paid."))
            invoice = Invoice.objects.get(id=request.POST.get('inv_id'))
            invoice.paid = True
            invoice.save()
            return redirect(invoices_all)

    return render(request, "invoices/all.jinja",
                  {
                      'unprocessed_events': Event.objects.filter(processed__isnull=True).count(),
                      'unpaid_invoices': Invoice.objects.filter(paid=False),
                      'all_invoices': Invoice.objects.all(),
                  })
