from django.test import TestCase
from django.urls import reverse

from ...society.tests import set_up_superuser, test_fixtures


class URLTests(TestCase):
    fixtures = test_fixtures
    HTTP_OK = 200

    @classmethod
    def setUpTestData(cls):
        set_up_superuser(cls)

    def setUp(self):
        self.client.force_login(self.user)

    def test_section_url_names(self):
        """
        Test that we can access the normal sections by their section names, and that they work.
        """
        views = ['overview', 'workers', 'events', 'invoices', 'wages', 'admin:index']
        for view in views:
            with self.subTest(msg="testing {view}".format(view=view)):
                self.assertEqual(self.client.get(reverse(view), follow=True).status_code, self.HTTP_OK)
