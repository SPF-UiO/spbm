from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, F
from django.db import models
from django.views.generic import TemplateView
from django.utils.translation import ugettext as _

from spbm.apps.society.models import Event, Invoice
from spbm.helpers.auth import user_society


class Overview(LoginRequiredMixin, TemplateView):
    """
    Currently very un-helpful class, but soon to contain useful things like number of invoices outstanding, days till
    next period, and what not!
    """
    template_name = 'index.jinja'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({
            'society': user_society(self.request),
            'dashboard': get_dashboard_information()
        })

        return context


def get_dashboard_information():
    invoices = Invoice.objects.all().order_by('-period')
    this_period = invoices[0]
    last_period = invoices[1]

    events = Event.objects.all()
    events_last_period = events.filter(invoice=last_period)
    events_this_period = events.filter(invoice=this_period)

    wages_this_period = (events.filter(invoice=this_period)
        .aggregate(wages=Sum(F('shifts__hours') * F('shifts__wage'),
                             output_field=models.DecimalField(decimal_places=2))))['wages']
    wages_last_period = (events.filter(invoice=last_period)
        .aggregate(wages=Sum(F('shifts__hours') * F('shifts__wage'),
                             output_field=models.DecimalField(decimal_places=2))))['wages']

    workers_this_period = (events.filter(invoice=last_period).select_related('shifts__worker')
        .distinct('shifts__worker')).count()
    workers_last_period = (events.filter(invoice=last_period).select_related('shifts__worker')
        .distinct('shifts__worker')).count()

    return [
        {'title': _("Events"),
         'kpi': events_this_period.count(),
         'change': change(events_last_period.count(), events_this_period.count()),
         'time': _("last period")},

        {'title': _("Wages"),
         'kpi': wages_this_period,
         'change': change(wages_last_period, wages_this_period),
         'time': _("last period")},

        {'title': _("Payroll Workers"),
         'kpi': workers_this_period,
         'change': change(workers_last_period, workers_this_period),
         'time': _("last term")},
    ]


def change(before, after):
    return ((before / after) - 1) * 100.00
