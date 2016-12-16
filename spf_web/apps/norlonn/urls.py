from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',
                       url(r'^$', views.index, name="norlonn"),
                       url(r'^generate_report/$', views.generate_report),
                       url(r'^get_report/(?P<date>.*)/$', views.get_report),
                       )
