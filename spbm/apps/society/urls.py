from django.conf.urls import url, include

# TODO: Create intermediate class to decouple Norlønn from wage reporting
from spbm.apps.norlonn import views as wages

from .views import views_overview as overview, views_workers as workers, \
    events, invoicing
from .views.views_overview import index as standard_index

# Our *pre-made* (*cough*) bit of URL that specifies which society we're in.
# Admittedly I feel like this ought to be scrapped, seeing as we could simply keep track of permitted societies
# in the session instead, allowing to change and keep the change between each.
society_match = r'(?P<society_name>[A-Za-z]+)/'

overview_urls = [
    url(r'^$', overview.index, name='index'),
]

workers_urls = [
    url(r'^$', workers.redirect_society, name='workers'),
    url(r'^' + society_match, include([
        url(r'^$', workers.index, name='workers-overview'),
        url(r'^add/$', workers.add, name='workers-add'),
        url(r'^edit/(?P<worker_id>\d+)$', workers.EditWorker.as_view(), name='workers-edit'),
    ])),
]

event_urls = [
    url(r'^$', events.index, name='events'),
    url(r'^add/$', events.EventCreateView.as_view(), name='events-add'),
    url(r'^edit/(?P<pk>\d+)$', events.EventUpdateView.as_view(), name='events-view'),
]

invoicing_urls = [
    url(r'^$', invoicing.InvoicingView.as_view(), name="invoices"),
    url(r'^$', invoicing.InvoicingView.as_view(), name="invoicing"),
    url(r'^view/' + society_match + r'(?P<date>\d{4}-\d{2}-\d{2})/$', invoicing.view_invoice, name='invoice-view'),
    url(r'^view/' + society_match + r'(?P<date>\d{4}-\d{2}-\d{2}).pdf$', invoicing.generate_pdf, name='invoice-view-pdf'),
]

wages_urls = [
    url(r'^$', wages.index, name="wages"),
    url(r'^generate_report/$', wages.generate_report, name="wages-generate_report"),
    url(r'^get_report/(?P<date>.*)/$', wages.get_report, name="wages-report"),
]

urlpatterns = [
    url(r'^$', standard_index),
    url(r'^society/', include(overview_urls)),
    url(r'^workers/', include(workers_urls)),
    url(r'^events/', include(event_urls)),
    url(r'^invoices/', include(invoicing_urls)),
    url(r'^wages/', include(wages_urls)),
]
