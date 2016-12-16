from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',
                       url(r'^$', views.redirect_society, name="invoices"),
                       url(r'^all/$', views.invoices_all, name="invoices-all"),
                       url(r'^list/$', views.invoices_list, name="invoices-list"),
                       url(r'^(?P<society_name>[A-Za-z]+)/$', views.index),
                       url(r'^(?P<society_name>[A-Za-z]+)/(?P<date>\d{4}-\d{2}-\d{2}).pdf$', views.generate),
                       )
