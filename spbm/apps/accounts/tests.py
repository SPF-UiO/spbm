from django.contrib.auth.models import User
from django.test import TestCase

from spbm.apps.accounts.backend import SPFBackend
from ..society.tests import test_fixtures


class AuthenticationTests(TestCase):
    fixtures = test_fixtures

    def test_various_logins(self):
        """
        Validate that our custom authentication backgrounds works when logins fail as well.
        """
        from django.contrib.auth import authenticate
        logins = [
            {
                'type': "valid user and pass",
                'user': 'rf',
                'pass': 'rf',
            },
            {
                'type': "invalid pass on admin",
                'user': 'admin',
                'pass': 'rf',
            },
            {
                'type': "invalid pass",
                'user': 'rf',
                'pass': 'notthepassword',
            },
            {
                'type': "invalid user",
                'user': 'newphone',
                'pass': 'rf',
            }]

        for login in logins:
            with self.subTest("trying {type}".format(type=login['type'])):
                attempt = authenticate(self.client.request(), username=login['user'], password=login['pass'])
                if login is logins[0]:
                    self.assertEqual(attempt, User.objects.get(username='rf'))
                else:
                    self.assertEqual(attempt, None)

    def test_invalid_pk_to_get_user(self):
        """
        Tests whether the backend successfully works, in returning a User when it should, and None when it shouldn't.
        Plus, it also ups our coverage a bit.
        """
        backend = SPFBackend()
        self.assertIsNone(backend.get_user(9999), "Invalid user should not exist according to backend and fixtures")
        self.assertIsNotNone(backend.get_user(1), "Valid user should exist according to backend and fixtures")
