from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
import debug_toolbar

from spbm.apps.society.views import PermissionDeniedView

handler403 = PermissionDeniedView.as_view()

urlpatterns = [
    # Django Debug Toolbar always included to make testing less fragile
    url(r"^__debug__/", include(debug_toolbar.urls)),
    url(r"^admin/", admin.site.urls),
    url(r"^accounts/", include("spbm.apps.accounts.urls")),
    url(r"^", include("spbm.apps.society.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
