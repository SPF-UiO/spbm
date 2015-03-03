from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
		url(r'^get_report/(?P<date>.*)/$', 'norlonn.views.get_report'),
)
