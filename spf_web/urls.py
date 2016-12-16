from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin

socurls = patterns('',
                   url(r'^$', include('spf_web.apps.society.urls')),
                   url(r'^society/', include('spf_web.apps.society.urls')),
                   url(r'^workers/', include('spf_web.apps.workers.urls')),
                   url(r'^events/', include('spf_web.apps.events.urls')),
                   url(r'^invoices/', include('spf_web.apps.invoices.urls')),
                   url(r'^norlonn/', include('spf_web.apps.norlonn.urls')),
                   )

urlpatterns = patterns('',
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^accounts/', include('spf_web.apps.accounts.urls')),
                       url(r'^society/', include('spf_web.apps.society.urls')),
                       url(r'^workers/', include('spf_web.apps.workers.urls')),
                       url(r'^events/', include('spf_web.apps.events.urls')),
                       url(r'^invoices/', include('spf_web.apps.invoices.urls')),
                       url(r'^norlonn/', include('spf_web.apps.norlonn.urls')),
                       # url(r'^(?P<society_name>[A-Za-z]+)/', include(socurls)),
                       url(r'^$', 'spf_web.apps.society.views.redirect_society')
                       ) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
