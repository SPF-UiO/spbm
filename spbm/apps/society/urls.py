from django.conf.urls import url, include

from .views import views_overview as overview, views_workers as workers, \
    views_events as events, views_invoicing as invoicing
from .views.views_overview import redirect_society as standard_index

# Our *pre-made* (*cough*) bit of URL that specifies which society we're in.
# Admittedly I feel like this ought to be scrapped, seeing as we could simply keep track of permitted societies
# in the session instead, allowing to change and keep the change between each.
society_match = r'^(?P<society_name>[A-Za-z]+)/'

society_urls = [
    url(r'^$', overview.redirect_society, name='society'),
    url(society_match + r'$', overview.index, name="index")
]

workers_urls = [
    url(r'^$', workers.redirect_society, name='workers'),
    url(society_match, include([
        url(r'^$', workers.index, name='workers-overview'),
        url(r'^add/$', workers.add, name='workers-add'),
        url(r'^edit/(?P<worker_id>\d+)$', workers.EditWorker.as_view(), name='workers-edit'),
    ])),
]

event_urls = [
    url(r'^$', events.redirect_society, name="events"),
    url(society_match + r'$', events.index, name="events-society"),
    url(society_match + r'add/$', events.add),
]

invoicing_urls = [
    url(r'^$', invoicing.redirect_society, name="invoices"),
    url(r'^all/$', invoicing.invoices_all, name="invoices-all"),
    url(r'^list/$', invoicing.invoices_list, name="invoices-list"),
    url(society_match + r'$', invoicing.index),
    url(society_match + r'(?P<date>\d{4}-\d{2}-\d{2})/$', invoicing.view_invoice),
    url(society_match + r'(?P<date>\d{4}-\d{2}-\d{2}).pdf$', invoicing.generate_pdf),
]

urlpatterns = [
    url(r'^$', standard_index),
    url(r'^society/', include(society_urls)),
    url(r'^workers/', include(workers_urls)),
    url(r'^events/', include(event_urls)),
    url(r'^invoices/', include(invoicing_urls)),
]
