from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models


class Event(models.Model):
    society = models.ForeignKey('society.Society', null=False, on_delete=models.PROTECT)
    name = models.CharField(max_length=100)
    date = models.DateField(verbose_name="Event date")
    registered = models.DateField(auto_now_add=True, editable=False)
    processed = models.DateField(null=True, blank=True)
    invoice = models.ForeignKey('invoices.Invoice', null=True, blank=True)

    def __str__(self):
        return self.society.shortname + " - " + str(self.date) + ": " + self.name

    def get_cost(self):
        total = Decimal(0)
        for s in self.shift_set.all():
            total += s.get_total()
        total = total.quantize(Decimal(".01"))
        return total

    get_cost.short_description = "Total cost"

    def clean(self):
        if self.invoice is not None:
            if self.invoice.society != self.society:
                raise ValidationError("Cannot add event to another society invoice!")


class Shift(models.Model):
    event = models.ForeignKey(Event)
    worker = models.ForeignKey('workers.Worker', on_delete=models.PROTECT)
    wage = models.DecimalField(max_digits=10, decimal_places=2)
    hours = models.DecimalField(max_digits=10, decimal_places=2)
    norlonn_report = models.ForeignKey('norlonn.NorlonnReport', blank=True, null=True, on_delete=models.SET_NULL)

    norlonn_report.short_description = "Sent to norlønn"

    class Meta:
        unique_together = ("event", "worker")

    def clean(self):
        try:
            if self.worker.society != self.event.society:
                raise ValidationError("Worker on shift does not belong to the same society as the event")
        except:
            raise ValidationError("No worker or event")

    def get_total(self):
        return (self.wage * self.hours).quantize(Decimal(".01"))
