from django.shortcuts import render
from django.http import HttpResponse

from events.models import Shift,Event
from decimal import Decimal

def get_report(request, date):
	events = Event.objects.filter(processed=date)
	linjer = []

	for e in events:
		shift = Shift.objects.filter(event=e)
		for s in shift:
			hours = s.hours*Decimal("100")
			hours = hours.quantize(Decimal("10"))
			wage = s.wage*Decimal("100")
			wage = wage.quantize(Decimal("10"))
			linjer.append(";"+str(s.worker.norlonn_number)+";H1;"+str(hours)+";"+str(wage)+";;")

	return HttpResponse("\n".join(linjer), content_type="text/plain")
# Create your views here.
