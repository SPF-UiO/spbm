from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from . import test_fixtures
from ..models import Event, Society
from ...accounts.models import SpfUser


class EventLoggedInTests(TestCase):
    fixtures = test_fixtures
    HTTP_OK = 200

    def setUp(self):
        self.user = User(username='kungfury')
        self.user.save()
        self.spf_user = SpfUser(user=self.user, society=Society.objects.get(pk=2))
        self.spf_user.save()
        self.client.force_login(self.user)

    def test_index(self):
        """
        Test the events index page returns a 200 with an empty list of processed events.
        """
        events_index = self.client.get(reverse('events'), follow=True)
        self.assertEqual(events_index.status_code, self.HTTP_OK)
        self.assertEqual(events_index.context['processed'].count(), 0)

    def test_can_access_logged_in(self):
        """
        Test that we can access these pages being logged in.
        """
        [self.assertEqual(self.client.get(reverse(view), follow=True).status_code, self.HTTP_OK,
                          "Incorrect HTTP response given!")
         for view in ['events', 'events-add']]

    def test_add_event(self):
        """
        Test that we can add an event.
        """
        event_data = {
            'name': "Magical Test Event",
            'date': "2017-01-25",
            'shifts-0-worker': 3,
            'shifts-0-wage': 128.00,
            'shifts-0-hours': 8,
            'shifts-TOTAL_FORMS': 1,
            'shifts-MIN_NUM_FORMS': 1,
            'shifts-INITIAL_FORMS': 0
        }
        adding_event = self.client.post(reverse('events-add'), event_data, follow=True)
        self.assertEqual(adding_event.status_code, self.HTTP_OK)
        last_event = Event.objects.last()
        self.assertEqual(last_event.name, "Magical Test Event")
        self.assertTrue(last_event.date)
        self.assertEqual(last_event.shifts.count(), 1)

    def test_add_event_duplicate_worker(self):
        """
        Test that we fail when adding a worker twice to an event.
        """
        event_data = {
            'name': "Magical Test Event",
            'date': "2017-01-25",
            'shifts-0-worker': 3,
            'shifts-0-wage': 128.00,
            'shifts-0-hours': 8,
            'shifts-1-worker': 3,
            'shifts-1-wage': 128.00,
            'shifts-1-hours': 8,
            'shifts-TOTAL_FORMS': 2,
            'shifts-MIN_NUM_FORMS': 1,
            'shifts-INITIAL_FORMS': 0
        }
        added_event = self.client.post(reverse('events-add'), event_data, follow=True)
        self.assertTrue(added_event.context['inlines'][0].non_form_errors())
        last_event = Event.objects.last()
        self.assertEqual(last_event.name, "Lørdagsparty")


class EventLoggedOutTests(TestCase):
    def test_cannot_access_logged_out(self):
        """
        Verify that endpoints cannot be accessed while logged out.
        In other words, verify that they forward to the login screen.
        """
        from ..urls import event_urls
        for view in event_urls:
            from django.urls import NoReverseMatch
            try:
                response = self.client.get(reverse(view.name))
            except NoReverseMatch:
                # Better way to try views with a single parameter?
                response = self.client.get(reverse(view.name, args=[1]))
            self.assertEqual(response.status_code,
                             302,
                             "Did not receive expected HTTP UNAUTHORIZED")
            self.assertTrue("/accounts/login" in response.url)
