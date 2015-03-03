from django.shortcuts import render
from django.http import HttpResponse

from events.models import Shift,Event
from decimal import Decimal

def get_report(request, date):
	events = Event.objects.filter(processed=date)
	linjer = []
	personshift = {}

	for e in events:
		shift = Shift.objects.filter(event=e)
		for s in shift:
			if s.worker.norlonn_number in personshift:
				personshift[s.worker.norlonn_number].append(s)
			else:
				personshift[s.worker.norlonn_number] = [s, ]
	print(str(personshift))
	for (nl,ss) in personshift.items():
		total = Decimal(0)
		
		for s in ss:
			total += s.hours*s.wage
	
		total = total*Decimal("100")	
		total = total.quantize(Decimal("10"))
		linjer.append(";"+str(s.worker.norlonn_number)+";H1;;;"+str(total))

	return HttpResponse("\n".join(linjer), content_type="text/plain")
# Create your views here.
