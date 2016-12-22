from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _


# class Event(models.Model):
#     society = models.ForeignKey('society.Society', null=False, on_delete=models.PROTECT)
#     name = models.CharField(max_length=100,
#                             verbose_name=_('name'))
#     date = models.DateField(verbose_name=_('event date'))
#     registered = models.DateField(auto_now_add=True,
#                                   editable=False,
#                                   verbose_name=_('registered'))
#     processed = models.DateField(null=True,
#                                  blank=True,
#                                  verbose_name=_('processed'))
#     invoice = models.ForeignKey('invoices.Invoice',
#                                 null=True,
#                                 blank=True,
#                                 verbose_name=_('invoice'))
#
#     def __str__(self):
#         return self.society.shortname + " - " + str(self.date) + ": " + self.name
#
#     def get_cost(self):
#         total = Decimal(0)
#         for s in self.shift_set.all():
#             total += s.get_total()
#         total = total.quantize(Decimal(".01"))
#         return total
#
#     get_cost.short_description = _("Total cost")
#
#     def clean(self):
#         if self.invoice is not None:
#             if self.invoice.society != self.society:
#                 raise ValidationError("Cannot add event to another society invoice!")
#
#
# class Shift(models.Model):
#     event = models.ForeignKey('society.Event')
#     worker = models.ForeignKey('society.Worker',
#                                on_delete=models.PROTECT,
#                                verbose_name=_('worker'))
#     wage = models.DecimalField(max_digits=10,
#                                decimal_places=2,
#                                verbose_name=_('wage'))
#     hours = models.DecimalField(max_digits=10,
#                                 decimal_places=2,
#                                 verbose_name=_('hours'))
#     norlonn_report = models.ForeignKey('norlonn.NorlonnReport',
#                                        blank=True,
#                                        null=True,
#                                        on_delete=models.SET_NULL,
#                                        verbose_name=_('norl&oslash;nn report'))
#
#     norlonn_report.short_description = "Sent to norlønn"
#
#     class Meta:
#         unique_together = ("event", "worker")
#
#     def clean(self):
#         try:
#             if self.worker.society != self.event.society:
#                 raise ValidationError("Worker on shift does not belong to the same society as the event")
#         except:
#             raise ValidationError("No worker or event")
#
#     def get_total(self):
#         return (self.wage * self.hours).quantize(Decimal(".01"))
