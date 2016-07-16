from django.conf.urls import patterns, url

urlpatterns = patterns('',
                       url(r'^$', 'events.views.redirect_society', name="events"),
                       url(r'^(?P<society_name>[A-Za-z]+)/$', 'events.views.index'),
                       url(r'^(?P<society_name>[A-Za-z]+)/add/$', 'events.views.add'),
                       )
