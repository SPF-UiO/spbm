from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin

from spbm.apps.society.views.views_overview import redirect_society as standard_index

urlpatterns = [
                  url(r'^admin/', admin.site.urls),
                  url(r'^accounts/', include('spbm.apps.accounts.urls')),
                  url(r'^norlonn/', include('spbm.apps.norlonn.urls')),
                  url(r'^society/', include('spbm.apps.society.urls')),
                  url(r'^workers/', include('spbm.apps.society.urls_workers')),
                  url(r'^events/', include('spbm.apps.society.urls_events')),
                  url(r'^invoices/', include('spbm.apps.society.urls_invoices')),
                  url(r'^$', standard_index),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
