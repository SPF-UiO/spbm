from django.conf.urls import url
from django.contrib.auth import views

urlpatterns = [
    url(r'^login/$', views.LoginView.as_view(template_name='accounts/login.jinja')),
    url(r'^logout/$', views.LogoutView.as_view(next_page='/'), name='logout'),
    url(r'^password_change/$', views.PasswordChangeView.as_view()),
    url(r'^password_reset/$', views.PasswordResetView.as_view()),
]
