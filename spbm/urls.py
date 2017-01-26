from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin

from spbm.apps.society.views import PermissionDeniedView

handler403 = PermissionDeniedView.as_view()

urlpatterns = [
                  url(r'^admin/', admin.site.urls),
                  url(r'^accounts/', include('spbm.apps.accounts.urls')),
                  url(r'^norlonn/', include('spbm.apps.norlonn.urls')),
                  url(r'^', include('spbm.apps.society.urls')),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
