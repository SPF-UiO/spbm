import re

from django import template
from django.urls import reverse, NoReverseMatch
from django.utils.safestring import mark_safe
from django_jinja import library
import jinja2


@library.global_function
@jinja2.contextfunction
def active(context, *active_names, attribute=False):
    """
    Allows you to specify tokens to receive 'active' attribute for.

    :param context: Passed by Django. Crucial.
    :param active_names: List of tokens to accept.
    :param attribute: Whether to return it with class=.., or if not, alone.
    :return: active if within, or none if not.
    """
    if len(active_names) < 1:
        raise template.TemplateSyntaxError("%r tag requires at least one argument" % active_names)

    path = template.Variable('request').resolve(context).path

    for url_name in active_names:
        try:
            pattern = '^' + reverse(url_name)
        except NoReverseMatch:
            pattern = url_name
        if re.search(pattern, path):
            if attribute:
                return mark_safe(' class="active"')
            else:
                return mark_safe(' active')
    return ""
