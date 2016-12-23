from django.conf.urls import url
from django.contrib.auth import views

urlpatterns = [
    url(r'^login/$', views.login, {'template_name': 'accounts/login.jinja'}),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^password_change/$', views.password_change),
    url(r'^password_reset/$', views.password_reset),
]
