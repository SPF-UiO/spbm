from django.conf.urls import url

from .views import views_overview

urlpatterns = [
    url(r'^$', views_overview.redirect_society, name='society'),
    url(r'^(?P<society_name>[A-Za-z]+)/$', views_overview.index, name="index")
]
