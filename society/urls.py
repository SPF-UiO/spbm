from django.conf.urls import patterns, include, url

import society.views

urlpatterns = patterns('',
                       url(r'^$', society.views.redirect_society, name='society'),
                       url(r'^(?P<society_name>[A-Za-z]+)/$', society.views.index, name="index"),
                       )
