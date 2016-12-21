from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect

from helpers.auth import user_allowed_society
from spf_web.apps.society.forms.worker import WorkerForm, WorkerEditForm
from spf_web.apps.society.models import Society, Worker


@login_required
def redirect_society(request):
    """
    Simply passes all requests to the index for the society, despite its lack of content.
    :param request:
    :return:
    """
    return redirect(index, society_name=request.user.spfuser.society.shortname)


@login_required
def index(request, society_name):
    society = get_object_or_404(Society, shortname=society_name)
    if not user_allowed_society(request.user, society):
        return render(request, "errors/unauthorized.jinja")

    workers = Worker.objects.filter(society=society).order_by("norlonn_number")
    inactive_workers = workers.filter(active=False)
    workers = workers.filter(active=True)
    return render(request, "workers/index.jinja",
                  {'workers': workers, 'cur_page': 'workers', 'form': WorkerForm(), 'post_url': 'add/',
                   'old_workers': inactive_workers})


@login_required
def add(request, society_name):
    society = get_object_or_404(Society, shortname=society_name)
    if not user_allowed_society(request.user, society):
        return render(request, "errors/unauthorized.jinja")

    worker = WorkerForm(request.POST)

    if worker.is_valid():
        worker_model = worker.save(commit=False)
        worker_model.society = society
        worker_model.save()
        return redirect(index, society_name=society_name)

    workers = Worker.objects.filter(society=society)
    return render(request, "workers/index.jinja",
                  {'workers': workers, 'cur_page': 'workers', 'form': worker, 'post_url': ''})


@login_required
def edit(request, society_name, worker_id):
    society = get_object_or_404(Society, shortname=society_name)
    if not user_allowed_society(request.user, society):
        return render(request, "errors/unauthorized.jinja")

    worker = get_object_or_404(Worker, id=worker_id)
    worker_form = WorkerEditForm(request.POST or None, instance=worker)

    if worker_form.is_valid():
        worker_form.save()
        return redirect(index, society_name=society.shortname)

    return render(request, "workers/edit.jinja", {'form': worker_form})
