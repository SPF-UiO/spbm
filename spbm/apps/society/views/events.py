from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.forms.formsets import formset_factory, all_valid
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from extra_views import CreateWithInlinesView, InlineFormSet, UpdateWithInlinesView

from spbm.helpers.auth import user_allowed_society, user_society
from ..forms.events import EventForm, make_shift_base
from ..models import Society, Event, Shift


@login_required
def index(request, society_name=None):
    society = request.user.spfuser.society if society_name is None \
        else get_object_or_404(Society, shortname=society_name)

    if not user_allowed_society(request.user, society):
        return render(request, "errors/unauthorized.jinja")

    events = Event.objects.filter(society=society)
    processed = events.values('processed').distinct().extra(select={'processed_is_null': 'processed IS NULL'},
                                                            order_by=['-processed_is_null', '-processed'])
    events_by_date = {}
    for event in processed:
        events_by_date[event['processed']] = events.filter(processed=event['processed']).order_by('-date')

    return render(request, "events/index.jinja",
                  {'processed': processed, 'events': events_by_date, 'cur_page': 'events'})


class ShiftInlineForm(InlineFormSet):
    model = Shift
    exclude = ['norlonn_report']
    can_delete = False

    def get_form_class(self):
        return make_shift_base(user_society(self.request))

    def get_factory_kwargs(self):
        kwargs = super(ShiftInlineForm, self).get_factory_kwargs()
        kwargs.update({
            'min_num': 1,
        })
        return kwargs


class EventCreateView(LoginRequiredMixin, CreateWithInlinesView):
    template_name = "events/add.jinja"
    model = Event
    fields = ['name', 'date']
    inlines = [ShiftInlineForm, ]

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)

        if form.is_valid():
            self.object = form.save(commit=False)
            self.object.society = user_society(request)
            form_validated = True
        else:
            self.object = None
            form_validated = False

        inlines = self.construct_inlines()

        if all_valid(inlines) and form_validated:
            return self.forms_valid(form, inlines)
        return self.forms_invalid(form, inlines)


class EventUpdateView(LoginRequiredMixin, UpdateWithInlinesView):
    template_name = "events/add.jinja"
    model = Event
    fields = ['name', 'date']
    inlines = [ShiftInlineForm, ]


@login_required
def add(request, society_name=None):
    society = request.user.spfuser.society if society_name is None \
        else get_object_or_404(Society, shortname=society_name)

    if not user_allowed_society(request.user, society):
        return render(request, "errors/unauthorized.jinja")

    event_form = formset_factory(EventForm, min_num=1, max_num=1)
    shift_form = formset_factory(make_shift_base(society), min_num=6, max_num=12)

    if request.method == "POST":
        event_formset = event_form(request.POST, prefix="event")
        shift_formset = shift_form(request.POST, prefix="shift")

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
                return redirect(index)
    else:
        event_formset = event_form(prefix="event")
        shift_formset = shift_form(prefix="shift")

    return render(request, "events/add.jinja", {'event_formset': event_formset, 'shift_formset': shift_formset})
