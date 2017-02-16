from django.conf import settings

test_fixtures = ['Event', 'Invoice', 'Shift', 'Society', 'Worker', 'NorlonnReport', 'User',
                 'SpfUser']


# Turn on the django-jinja template debug to provide response.context in the client.
# NOTE: Do *not* change any other settings on-the-fly. This one only affects this exact issue,
#       and as such it's safe to edit. Otherwise Django settings are _immutable_.
settings.TEMPLATES[0]['OPTIONS']['debug'] = True
