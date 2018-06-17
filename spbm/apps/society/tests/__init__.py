from django import test
from django.conf import settings
from django.contrib.auth.models import User

from spbm.apps.accounts.models import SpfUser
from spbm.apps.society.models import Society

test_fixtures = ['Event', 'Invoice', 'Shift', 'Society', 'Worker', 'Employment', 'NorlonnReport', 'User',
                 'SpfUser']

# Turn on the django-jinja template debug to provide response.context in the client.
# NOTE: Do *not* change any other settings on-the-fly. This one only affects this exact issue,
#       and as such it's safe to edit. Otherwise Django settings are _immutable_.
# SECOND NOTE: This only applies during testing.
settings.TEMPLATES[0]['OPTIONS']['debug'] = True


class SPFTestMixin(test.SimpleTestCase):
    """
    Helper for tests, use as a mix-in to add any extra assertions.
    """

    def assertMessagesContains(self, response, needle: str, msg=None):
        if not any(needle in str(x) for x in list(response.context['messages'])):
            msg = self._formatMessage(msg, "'%s' not contained in messages" % needle)
            raise self.failureException(msg)


def set_up_superuser(self: test.SimpleTestCase) -> None:
    """
    Helper to setup a superuser for when you need one. Use from setUpTestCase.
    :param self:
    """
    # Create the user and add the needed permissions
    self.user = User(username='superfury', is_superuser=True)
    self.user.save()
    # set him as part of a society, then force login
    self.spf_user = SpfUser(user=self.user, society=Society.objects.get(pk=1))
    self.spf_user.save()
