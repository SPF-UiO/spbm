from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',
                       url(r'^$', views.redirect_society, name='society'),
                       url(r'^(?P<society_name>[A-Za-z]+)/$', views.index, name="index"),
                       )
