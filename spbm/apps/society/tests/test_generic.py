from django.test import SimpleTestCase
from django.urls import reverse


class URLTests(SimpleTestCase):
    HTTP_OK = 200

    def test_section_url_names(self):
        """
        Test that we can access the normal sections by their section names, and that they work.
        """
        views = ['overview', 'workers', 'events', 'invoices', 'wages', 'admin:index']
        for view in views:
            with self.subTest(msg="testing {view}".format(view=view)):
                self.assertEqual(self.client.get(reverse(view), follow=True).status_code, self.HTTP_OK)
