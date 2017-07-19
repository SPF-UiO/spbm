import itertools

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms.formsets import all_valid
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.utils.translation import ugettext as _
from django.views.generic import DetailView, DeleteView
from extra_views import CreateWithInlinesView, InlineFormSet, UpdateWithInlinesView

from spbm.helpers.auth import user_society
from spbm.helpers.mixins import LoginAndPermissionRequiredMixin
from ..forms.events import make_shift_base, EventForm
from ..models import Society, Event, Shift


@login_required
def index(request, society_name=None):
    society = request.user.spfuser.society if society_name is None \
        else get_object_or_404(Society, shortname=society_name)

    """ Create another field so that we can order first the processed = None events, then the processed ones in 
        the reverse order, e.g. descending """
    # TODO: Create another Manager, or tweak the query to annotate the cost right here and now.
    society_events = Event.objects.filter(society=society) \
        .prefetch_related('shifts__worker') \
        .extra(select={'processed_is_null': 'processed IS NULL'},
               order_by=['-processed_is_null', '-processed'])

    grouped_events = []
    for date, event in itertools.groupby(society_events, lambda x: x.processed):
        grouped_events.append((date, list(event)))
    return render(request, "events/index.jinja", {'events': grouped_events})


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


class CreateEvent(LoginAndPermissionRequiredMixin, CreateWithInlinesView):
    template_name = "events/add.jinja"
    permission_required = 'society.add_event'
    permission_denied_message = _("You are not allowed to create events due to lacking permissions.")
    model = Event
    form_class = EventForm
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


class UpdateEvent(LoginAndPermissionRequiredMixin, UpdateWithInlinesView):
    template_name = "events/edit.jinja"
    permission_required = 'society.change_event'
    permission_denied_message = _("You are not allowed to edit events due to lacking permissions.")
    model = Event
    form_class = EventForm
    inlines = [ShiftInlineForm, ]


class ViewEvent(LoginRequiredMixin, DetailView):
    template_name = "events/view.jinja"
    model = Event
    queryset = Event.objects.filter(society_id=1)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = context['object']
        next = event.get_next_by_date()
        previous = event.get_previous_by_date()
        return context

class DeleteEvent(LoginRequiredMixin, DeleteView):
    template_name = "delete.jinja"
    model = Event
    success_url = reverse_lazy('events')
    queryset = Event.objects.filter(processed__isnull=True)
