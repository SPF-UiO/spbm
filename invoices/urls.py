from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
		url(r'^$', 'invoices.views.redirect_society', name="invoices"),
		url(r'^all/$', 'invoices.views.invoices_all', name="invoices-all"),
		url(r'^list/$', 'invoices.views.invoices_list', name="invoices-list"),
		url(r'^(?P<society_name>[A-Za-z]+)/$', 'invoices.views.index'),
		url(r'^(?P<society_name>[A-Za-z]+)/(?P<date>\d{4}-\d{2}-\d{2}).pdf$', 'invoices.views.generate'),
)
