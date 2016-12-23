from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name="norlonn"),
    url(r'^generate_report/$', views.generate_report),
    url(r'^get_report/(?P<date>.*)/$', views.get_report),
]
