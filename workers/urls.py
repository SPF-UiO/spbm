from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
                       url(r'^$', 'workers.views.redirect_society', name='workers'),
                       url(r'^(?P<society_name>[A-Za-z]+)/$', 'workers.views.index'),
                       url(r'^(?P<society_name>[A-Za-z]+)/add/$', 'workers.views.add'),
                       url(r'^(?P<society_name>[A-Za-z]+)/edit/(?P<worker_id>\d+)$', 'workers.views.edit'),
                       )
