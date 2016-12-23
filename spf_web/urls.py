from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin

from spf_web.apps.society.views.views_overview import redirect_society as standard_index

urlpatterns = [
                  url(r'^admin/', admin.site.urls),
                  url(r'^accounts/', include('spf_web.apps.accounts.urls')),
                  url(r'^norlonn/', include('spf_web.apps.norlonn.urls')),
                  url(r'^society/', include('spf_web.apps.society.urls')),
                  url(r'^workers/', include('spf_web.apps.society.urls_workers')),
                  url(r'^events/', include('spf_web.apps.society.urls_events')),
                  url(r'^invoices/', include('spf_web.apps.society.urls_invoices')),
                  url(r'^$', standard_index),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
