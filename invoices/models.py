from django.db import models
from events.models import Event
from decimal import Decimal

class Invoice(models.Model):
	society = models.ForeignKey('society.Society')
	invoice_number = models.IntegerField(unique=True)
	period = models.DateField()
	paid = models.BooleanField(default=False)


	class Meta:
		unique_together = ('period', 'society')
		permissions = (
			('close_period', "Can close periods to generate invoices"),
			('mark_paid', "Can mark invoices as paid")
		)

	def get_total_cost(self):
		cost = 0
		events = Event.objects.filter(invoice=self)

		for event in events:
			cost += event.get_cost()

		return cost*Decimal('1.3')

	def __str__(self):
		return "Number: "+str(self.invoice_number)+": "+str(self.period)

