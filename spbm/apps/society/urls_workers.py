from django.conf.urls import url

from .views import views_workers

urlpatterns = [
    url(r'^$', views_workers.redirect_society, name='workers'),
    url(r'^(?P<society_name>[A-Za-z]+)/$', views_workers.index),
    url(r'^(?P<society_name>[A-Za-z]+)/add/$', views_workers.add),
    url(r'^(?P<society_name>[A-Za-z]+)/edit/(?P<worker_id>\d+)$', views_workers.edit),
]
