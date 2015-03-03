from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic.base import RedirectView

socurls = patterns('',
	url(r'^$', include('society.urls')),
	url(r'^society/', include('society.urls')),
	url(r'^workers/', include('workers.urls')),
	url(r'^events/', include('events.urls')),
	url(r'^invoices/', include('invoices.urls')),
	url(r'^norlonn/', include('norlonn.urls')),
)

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
		url(r'^accounts/', include('accounts.urls')),
		url(r'^society/', include('society.urls')),
		url(r'^workers/', include('workers.urls')),
		url(r'^events/', include('events.urls')),
		url(r'^invoices/', include('invoices.urls')),
		url(r'^norlonn/', include('norlonn.urls')),
		#url(r'^(?P<society_name>[A-Za-z]+)/', include(socurls)),
		url(r'^$', 'society.views.redirect_society')
)
