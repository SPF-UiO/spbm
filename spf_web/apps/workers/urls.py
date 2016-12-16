from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',
                       url(r'^$', views.redirect_society, name='workers'),
                       url(r'^(?P<society_name>[A-Za-z]+)/$', views.index),
                       url(r'^(?P<society_name>[A-Za-z]+)/add/$', views.add),
                       url(r'^(?P<society_name>[A-Za-z]+)/edit/(?P<worker_id>\d+)$', views.edit),
                       )
