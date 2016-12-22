from django.conf.urls import patterns, url

from .views import views_invoicing

urlpatterns = patterns('',
                       url(r'^$', views_invoicing.redirect_society, name="invoices"),
                       url(r'^all/$', views_invoicing.invoices_all, name="invoices-all"),
                       url(r'^list/$', views_invoicing.invoices_list, name="invoices-list"),
                       url(r'^(?P<society_name>[A-Za-z]+)/$', views_invoicing.index),
                       url(r'^(?P<society_name>[A-Za-z]+)/(?P<date>\d{4}-\d{2}-\d{2}).pdf$', views_invoicing.generate),
                       )
