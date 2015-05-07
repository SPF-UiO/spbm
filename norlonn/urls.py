from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
		url(r'^$', 'norlonn.views.index'),
		url(r'^generate_report/$', 'norlonn.views.generate_report'),
		url(r'^get_report/(?P<date>.*)/$', 'norlonn.views.get_report'),
)
