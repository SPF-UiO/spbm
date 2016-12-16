from django.conf.urls import patterns, url

urlpatterns = patterns('',
                       url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'accounts/login.jinja'}),
                       url(r'^logout/$', 'django.contrib.auth.views.logout', name='logout'),
                       url(r'^password_change/$', 'django.contrib.auth.views.password_change'),
                       url(r'^password_reset/$', 'django.contrib.auth.views.password_reset'),
                       )
