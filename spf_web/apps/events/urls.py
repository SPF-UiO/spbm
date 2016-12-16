from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',
                       url(r'^$', views.redirect_society, name="events"),
                       url(r'^(?P<society_name>[A-Za-z]+)/$', views.index),
                       url(r'^(?P<society_name>[A-Za-z]+)/add/$', views.add),
                       )
