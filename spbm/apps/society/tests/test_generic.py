from django.test import TestCase, SimpleTestCase
from django.urls import reverse


class URLTests(SimpleTestCase):

    def test_section_url_names(self):
        self.assertEqual(self.client.get(reverse('index'), follow=True).status_code, 200)
        self.assertEqual(self.client.get(reverse('workers'), follow=True).status_code, 200)
        self.assertEqual(self.client.get(reverse('events'), follow=True).status_code, 200)
        self.assertEqual(self.client.get(reverse('invoices'), follow=True).status_code, 200)
        self.assertEqual(self.client.get(reverse('wages'), follow=True).status_code, 200)


