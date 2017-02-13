from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from spbm.helpers.auth import user_allowed_society
from ..models import Society


@login_required
def redirect_society(request):
    """
    Simply passes all requests to the index for the society, despite its lack of content.
    :param request:
    :return:
    """
    return redirect(index, society_name=request.user.spfuser.society.shortname)


@login_required
def index(request):
    society = request.user.spfuser.society
    if not user_allowed_society(request.user, society):
        return render(request, "errors/unauthorized.jinja")

    return render(request, "society/index.jinja",
                  {'society': society, 'cur_page': 'society'})
