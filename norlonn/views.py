from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required,user_passes_test

from events.models import Shift,Event
from decimal import Decimal
from norlonn.models import NorlonnReport

@login_required
def index(request):
	reports = NorlonnReport.objects.all().order_by('-date')
	errors = []

	for s in Shift.objects.filter(norlonn_report__isnull=True, event__processed__isnull=False):
		if s.worker.norlonn_number is None:
			errors.append("Worker %s lacks norlonn number!" % s.worker)

		if s.event.invoice.paid == False:
			errors.append("Invoice not paid for worker %s" % s.worker)

	return render(request, 'norlonn/index.jinja', { 'reports': reports, 'errors': errors })

@login_required
@user_passes_test(lambda u: u.is_superuser)
def generate_report(request):
	if request.method != "POST":
		return redirect(index)

	errors = []
	succ = []
	shifts = Shift.objects.filter(norlonn_report__isnull=True, event__processed__isnull=False)

	if not shifts.exists():
		return HttpResponse("Nothing to generate!")

	if NorlonnReport.objects.filter(date=timezone.now()).exists():
		return HttpResponse("Already exists!")

	report = NorlonnReport(date=timezone.now())
	report.save()
	
	for s in shifts:
		if s.worker.norlonn_number is None:
			errors.append("ERR: %s - %s --- Lacks norlonn number" % (s.worker, s.event))
			continue
		
		if s.event.invoice.paid == False:
			errors.append("ERR: %s - %s --- Invoice not paid" % (s.worker, s.event))
			continue

		succ.append("OK: %s - %s" % (s.worker, s.event))
		s.norlonn_report = report
		s.save()

	if len(succ) == 0:
		report.delete()
		return HttpResponse("Nothing to generate!");

	return render(request, 'norlonn/report.jinja', { 'errors': errors, 'success': succ })	

@login_required
def get_report(request, date):
	nr = get_object_or_404(NorlonnReport, date=date)
	linjer = []
	personshift = {}

	shift = Shift.objects.filter(norlonn_report=nr)
	for s in shift:
		if s.worker.norlonn_number in personshift:
			personshift[s.worker.norlonn_number].append(s)
		else:
			personshift[s.worker.norlonn_number] = [s, ]
	
	for (nl,ss) in personshift.items():
		total = Decimal(0)
		
		for s in ss:
			total += s.hours*s.wage
	
		total = total*Decimal("100")	
		total = total.quantize(Decimal("10"))
		linjer.append(";"+str(s.worker.norlonn_number)+";H1;100;"+str(total)+";")

	return HttpResponse("\n".join(linjer), content_type="text/plain; charset=utf-8")
# Create your views here.
