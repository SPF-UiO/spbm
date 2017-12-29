from django.urls import path, re_path, include

from spbm.apps.norlonn import views as wages
from .views import views_overview as overview, workers, \
    events, invoicing
from .views.views_overview import index as standard_index

# TODO: Create intermediate class to decouple current wage system from wage reporting

# Our *pre-made* (*cough*) bit of URL that specifies which society we're in.
# Admittedly I feel like this ought to be scrapped, seeing as we could simply keep track of permitted societies
# in the session instead, allowing to change and keep the change between each.
society_match = r'(?P<society_name>[A-Za-z]+)/'

overview_urls = [
    path('', overview.index, name='index'),
]

workers_urls = [
    path('', workers.redirect_society, name='workers'),
    re_path(r'^' + society_match, include([
        path('', workers.IndexWorker.as_view(), name='workers-overview'),
        path('add/', workers.AddWorker.as_view(), name='worker-add'),
        path('create/', workers.CreateWorker.as_view(), name='worker-create'),
        path('create/<int:nid>/', workers.CreateWorker.as_view(), name='worker-create'),
    ])),
    path('edit/<int:pk>/', workers.UpdateWorker.as_view(), name='worker-edit'),
    path('view/<int:pk>/', workers.ViewWorker.as_view(), name='worker-view'),
    path('delete/<int:pk>/', workers.DeleteWorker.as_view(), name='worker-delete'),
]

event_urls = [
    re_path(r'^$', events.index, name='events'),
    path('add/', events.CreateEvent.as_view(), name='event-add'),
    path('view/<int:pk>/', events.ViewEvent.as_view(), name='event-view'),
    path('edit/<int:pk>/', events.UpdateEvent.as_view(), name='event-edit'),
    path('delete/<int:pk>/', events.DeleteEvent.as_view(), name='event-delete'),
]

invoicing_urls = [
    re_path(r'^$', invoicing.InvoicingView.as_view(), name="invoices"),
    re_path(r'^$', invoicing.InvoicingView.as_view(), name="invoicing"),
    re_path(r'^view/' + society_match + r'(?P<date>\d{4}-\d{2}-\d{2})/$', invoicing.view_invoice, name='invoice-view'),
    re_path(r'^view/' + society_match + r'(?P<date>\d{4}-\d{2}-\d{2}).pdf$', invoicing.generate_pdf,
            name='invoice-view-pdf'),
]

wages_urls = [
    path('', wages.index, name="wages"),
    path('generate/', wages.generate_report, name="wages-generate_report"),
    path('export/<str:date>/', wages.get_report, name="wages-report"),
]

urlpatterns = [
    path('', standard_index),
    path('society/', include(overview_urls)),
    path('workers/', include(workers_urls)),
    path('events/', include(event_urls)),
    path('invoices/', include(invoicing_urls)),
    path('wages/', include(wages_urls)),
]
