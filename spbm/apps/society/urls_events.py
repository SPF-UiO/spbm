from django.conf.urls import url

from .views import views_events

urlpatterns = [
    url(r'^$', views_events.redirect_society, name="events"),
    url(r'^(?P<society_name>[A-Za-z]+)/$', views_events.index),
    url(r'^(?P<society_name>[A-Za-z]+)/add/$', views_events.add),
]
