from django.shortcuts import render,get_object_or_404,redirect
from helpers.auth import user_allowed_society
from django.contrib.auth.decorators import login_required

from django.forms.formsets import formset_factory
from events.forms import EventForm,MakeShiftBase

from society.models import Society
from events.models import Event,Shift

from django.db import transaction

@login_required
def redirect_society(request):
	return redirect(index, society_name=request.user.spfuser.society.shortname)

@login_required
def index(request, society_name):
	society = Society.objects.get(shortname=society_name)
	if not user_allowed_society(request.user, society):
		return render(request, "errors/unauthorized.jinja")

	events = Event.objects.filter(society=society)
	proc_vals = events.values('processed').distinct().extra(select={'processed_is_null': 'processed IS NULL'}, order_by=['-processed_is_null', '-processed'])
	
	eset = {}
	for p in proc_vals:
		eset[p['processed']] = events.filter(processed=p['processed']).order_by('-date')
	
	return render(request, "events/index.jinja", { 'processed': proc_vals, 'events': eset, 'cur_page': 'events'})

@login_required
def add(request, society_name):
	society = Society.objects.get(shortname=society_name)
	if not user_allowed_society(request.user, society):
		return render(request, "errors/unauthorized.jinja")

	eventform = formset_factory(EventForm, min_num=1, max_num=1)
	shiftform = formset_factory(MakeShiftBase(society), min_num=6)

	if request.method == "POST":
		event_formset = eventform(request.POST, prefix="event")
		shift_formset = shiftform(request.POST, prefix="shift")
		
		if event_formset.is_valid():
			with transaction.atomic():
				event = event_formset[0].save(commit=False)
				event.society = society
				event.save()

				for shift in shift_formset:
					if not shift.is_valid():	
						continue

					if "worker" not in shift.cleaned_data:
						continue
					
					print(shift.cleaned_data['worker'])
					db_shift = Shift()	
					db_shift.event = event
					db_shift.worker = shift.cleaned_data['worker']
					db_shift.wage = shift.cleaned_data['wage']
					db_shift.hours = shift.cleaned_data['hours']
					db_shift.save()
				return redirect(index, society_name=society_name)
	else:
		event_formset = eventform(prefix="event")
		shift_formset = shiftform(prefix="shift")


	return render(request, "events/add.jinja", {'event_formset': event_formset, 'shift_formset': shift_formset})


	


	

