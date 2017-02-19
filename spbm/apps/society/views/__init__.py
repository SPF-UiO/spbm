from django.http import HttpResponseForbidden
from django.shortcuts import render
from django.views import View

from . import views_overview, views_workers


class PermissionDeniedView(View):
    """
    Renders a simple page to show that you've got a permission denied!
    """
    template_name = 'errors/unauthorized.jinja'

    def dispatch(self, request, *args, **kwargs):
        return HttpResponseForbidden(render(request, self.template_name, kwargs, *args))
