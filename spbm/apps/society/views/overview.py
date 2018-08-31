from decimal import Decimal
from typing import List

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models
from django.db.models import Sum, F, Min
from django.urls import reverse
from django.utils.translation import ugettext as _
from django.views.generic import TemplateView

from spbm.apps.society.models import Event, Invoice, Worker
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
            'dashboard': {
                'general': self.get_general_status_blocks(),
                'actionable': self.get_actionable_blocks()
            }
        })

        return context

    def get_general_status_blocks(self):
        # Get the invoices, but make sure it's not empty -- if we're getting the last one we need there to be something
        invoices = Invoice.objects.all().order_by('-period')
        last_period = invoices[0] if len(invoices) != 0 else None

        # FIXME: society invoices are currently not in use
        society_invoices = invoices.filter(society=user_society(self.request))

        events = Event.objects.all().select_related('shifts__worker')
        events_last_period = events.filter(invoice=last_period)
        events_this_period = events.filter(invoice=None)

        wages_this_period = (events_this_period
                             .aggregate(wages=Sum(F('shifts__hours') * F('shifts__wage'),
                                                  output_field=models.DecimalField(decimal_places=2))))['wages']
        wages_last_period = (events_last_period
                             .aggregate(wages=Sum(F('shifts__hours') * F('shifts__wage'),
                                                  output_field=models.DecimalField(decimal_places=2))))['wages']

        # workers_this_period = (events.filter(invoice=last_period).select_related('shifts__worker')
        #                        .distinct('shifts__worker')).count()
        workers_this_period = (events_this_period
                               .values('shifts__worker')).annotate(shifts=Min('shifts__worker')).count()
        # workers_last_period = (events.filter(invoice=last_period).select_related('shifts__worker')
        #                        .distinct('shifts__worker')).count()
        workers_last_period = (events_last_period
                               .values('shifts__worker')).annotate(shifts=Min('shifts__worker')).count()

        return self._sanitise_blocks([
            {'title': _("Events"),
             'kpi': events_this_period.count(),
             'change': change(events_last_period.count(), events_this_period.count()),
             'time': _("last period"),
             'url': reverse('events')},

            {'title': _("Wages"),
             'kpi': wages_this_period,
             'change': change(wages_last_period, wages_this_period),
             'time': _("last period"),
             'url': reverse('wages')},

            {'title': _("Workers"),
             'kpi': workers_this_period,
             'change': change(workers_last_period, workers_this_period),
             'time': _("last period"),
             'url': reverse('workers')},
        ])

    def get_actionable_blocks(self):
        blocked_wages = (Event.objects
                         .filter(society=user_society(self.request), invoice__paid=False)
                         .aggregate(wages=Sum(F('shifts__hours') * F('shifts__wage'),
                                              output_field=models.DecimalField(decimal_places=2))))['wages']
        missing_ids = (Worker.objects
                       .filter(employment__society=user_society(self.request), norlonn_number__isnull=True).count())

        return self._sanitise_blocks([
            {'title': _("Your Blocked Wages"),
             'kpi': blocked_wages if blocked_wages else None,
             'detail': _("Wages blocked by unpaid invoices"),
             'url': reverse('invoices'),
             'alert': 'success'},

            {'title': _("Your Missing Norlønn-IDs"),
             'kpi': missing_ids if missing_ids else None,
             'detail': _("Workers whose pay will not be exported"),
             'url': reverse('workers')}
        ])

    @staticmethod
    def _sanitise_blocks(blocks: List[dict]) -> List[dict]:
        """ Quick sanitising of two variable values in returned dict """
        for block in blocks:
            kpi = block.get('kpi') if block.get('kpi') is not None else 0
            # change = block.get('change') if block.get('change') is not Noneblock.setdefault('change', None)
            block.update(kpi=kpi)

        return blocks


def change(before: Decimal, after: Decimal):
    return Decimal(((before / after) - 1)) * Decimal(100.00) \
        if after != 0 and before is not None and after is not None else None
