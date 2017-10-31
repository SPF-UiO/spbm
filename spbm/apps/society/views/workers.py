from django.contrib import messages as msg
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.translation import ugettext as _
from django.views.generic import UpdateView, CreateView, DetailView, DeleteView, FormView, TemplateView
from django.views.generic.edit import FormMixin

from spbm.apps.society.forms.workers import WorkerForm, WorkerEditForm, WorkerPersonIDForm
from spbm.apps.society.models import Society, Worker, Employment
from spbm.helpers.auth import user_allowed_society, user_society
from spbm.helpers.mixins import LoginAndPermissionRequiredMixin


@login_required
def redirect_society(request):
    """
    Simply passes all requests to the index for the society, despite its lack of content.
    """
    return redirect('workers-overview', society_name=request.user.spfuser.society.shortname)


class IndexWorker(LoginRequiredMixin, FormMixin, TemplateView):
    template_name = 'workers/index.jinja'
    form_class = WorkerPersonIDForm
    # show "Permission denied" rather than redirect to login page
    raise_exception = True

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not request.user.has_perms(['society.add_worker', 'society.add_employment']):
            return self.handle_no_permission()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        # Get the society from the keyword arguments, via URLconf
        society = get_object_or_404(Society, shortname=self.kwargs['society_name'])

        workers = Worker.objects.filter(employment__society=society)\
            .select_related().order_by("norlonn_number").distinct()
        context = super().get_context_data()
        context.update({
            'inactive_workers': workers.filter(employment__active=False),
            'active_workers': workers.filter(employment__active=True),
            'society': society,
        })
        return context

    def form_valid(self, form):
        worker = Worker.objects.filter(person_id=form.cleaned_data['person_id']).first()
        society = user_society(self.request)
        if worker and society in worker.societies.all():
            msg.info(self.request,
                     _('{worker} is already associated with your society {society}.')
                     .format(worker=worker, society=society))
            return redirect(worker)
        elif worker:
            employment = Employment(society=society, worker=worker)
            employment.save()
            msg.success(self.request,
                        _('The worker {worker} has been successfully associated as employed with {society}.')
                        .format(worker=worker, society=society))
            return redirect(worker)
        else:
            msg.info(self.request,
                     _('There is no worker with that national ID. You may create one now.'))
            return redirect('worker-create', society_name=society, nid=form.cleaned_data['person_id'])


class CreateWorker(LoginAndPermissionRequiredMixin, CreateView):
    template_name = 'workers/create.jinja'
    permission_required = 'society.add_worker'
    permission_denied_message = _('You do not have the required permission to create workers.')
    model = Worker
    form_class = WorkerForm

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if self.kwargs.get('nid') and form.fields['person_id'].initial is None:
            form.fields['person_id'].initial = self.kwargs.get('nid')
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'society': get_object_or_404(Society, shortname=self.kwargs['society_name']),
        })
        return context

    def form_valid(self, form):
        society = get_object_or_404(Society, shortname=self.kwargs['society_name'])

        self.object = form.save()
        employment = Employment(worker=self.object, society=society)
        employment.save()
        return super().form_valid(form)


class UpdateWorker(LoginAndPermissionRequiredMixin, UpdateView):
    """
    Provides a simple editing interface for workers using #UpdateView.
    """
    model = Worker
    template_name = 'workers/edit.jinja'
    form_class = WorkerEditForm
    success_url = reverse_lazy('workers')
    raise_exception = True
    permission_denied_message = _('You do not have the permission to edit workers belonging to other societies.')

    def has_permission(self):
        return self.request.user.has_perm('society.change_worker') \
               and user_allowed_society(self.request.user, self.get_object().societies)


class ViewWorker(LoginAndPermissionRequiredMixin, DetailView):
    template_name = 'workers/view.jinja'
    permission_denied_message = _('You do not have the permission to view workers belonging to other societies.')
    model = Worker

    def has_permission(self):
        # FIXME: Creates an overhead of two extra queries per viewing :(
        return user_allowed_society(self.request.user, self.get_object().societies)


class DeleteWorker(LoginAndPermissionRequiredMixin, DeleteView):
    template_name = 'delete.jinja'
    model = Worker
    success_url = reverse_lazy('workers')
    queryset = Worker.objects.filter(shifts__isnull=True)

    def has_permission(self):
        return self.request.user.has_perm('society.delete_worker') \
               and user_allowed_society(self.request.user, self.get_object().societies)


""" 
Workflow for adding a user, which ties into CreateWorker.
"""


class AddWorker(LoginAndPermissionRequiredMixin, FormView):
    template_name = 'workers/add.jinja'
    permission_required = 'society.add_worker'
    form_class = WorkerPersonIDForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'society': get_object_or_404(Society, shortname=self.kwargs['society_name']),
        })
        return context

    def form_valid(self, form):
        national_id = form.cleaned_data['person_id']
        worker = Worker.objects.filter(person_id=national_id).first()
        if worker:
            return HttpResponseRedirect(reverse_lazy('worker-associate', args=[worker.pk]))
        else:
            return HttpResponseRedirect(reverse_lazy('worker-create',
                                                     kwargs={'society_name': self.kwargs['society_name'],
                                                             'nid': national_id}))
