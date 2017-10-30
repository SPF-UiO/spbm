from django.contrib.auth.models import User, Permission
from django.test import TestCase
from django.urls import reverse

from spbm.apps.accounts.models import SpfUser
from spbm.apps.society.models import Society, Worker
from . import test_fixtures, SPFTest


class WorkerTests(SPFTest, TestCase):
    fixtures = test_fixtures

    @classmethod
    def setUpTestData(cls):
        cls.test = True
        cls.society_name = 'CYB'
        cls.last_fixtures_worker = Worker.objects.last()

    def setUp(self):
        # Logging into the site as a test in itself can be somewhere else. This doesn't need it.
        self.user = User(username='cyb')
        self.user.save()
        self.spf_user = SpfUser(user=self.user, society=Society.objects.get(shortname=self.society_name))
        self.spf_user.save()
        self.client.force_login(self.user)

    def test_create_minimum_worker(self):
        """
        Creates the smallest worker possible.
        """
        worker = {
            'name': 'Ola Normann',
            'address': 'Adressegata 1, 0123 Oslo',
        }
        # Confirm that permissions stop us
        self.assertEqual(self.client.post(reverse('worker-create', args=[self.society_name]), data=worker).status_code,
                         403)
        # Confirm that adding permissions actually works
        self.user.user_permissions.add(Permission.objects.get(codename='add_worker'))
        post = self.client.post(reverse('worker-create', args=[self.society_name]), data=worker, follow=True)
        self.assertNotEqual(self.last_fixtures_worker, Worker.objects.last())
        self.assertEqual(post.status_code, 200)

    def test_create_full_worker(self):
        """
        Creates a worker with all the fields.
        """
        worker = {
            'name': 'Ola Normann',
            'norlonn_number': '100',
            'address': 'Adressegata 1, 0123 Oslo',
            'account_no': '1100.12.34562',
            'person_id': '01020394311',
        }
        self.user.user_permissions.add(Permission.objects.get(codename='add_worker'))
        post = self.client.post(reverse('worker-create', args=[self.society_name]), data=worker, follow=True)
        self.assertNotEqual(self.last_fixtures_worker, Worker.objects.last())
        self.assertEqual(post.status_code, 200)

    def test_create_worker_invalid_account_number(self):
        """
        Tries to create a worker with an invalid account number.
        """
        worker = {
            'name': 'Ola Normann',
            'address': 'Adressegata 1, 0123 Oslo',
            # off by one, so to speak
            'account_no': '1100.12.34563',
        }
        self.user.user_permissions.add(Permission.objects.get(codename='add_worker'))
        post = self.client.post(reverse('worker-create', args=[self.society_name]), data=worker, follow=True)
        self.assertEqual(self.last_fixtures_worker, Worker.objects.last())
        self.assertFormError(post, "form", "account_no",
                             "Invalid control digit. Enter a valid Norwegian bank account number.")
        self.assertEqual(post.status_code, 200)

    def test_create_worker_duplicate_norlonn(self):
        """
        Tries to create a worker with a duplicate national ID.
        """
        self.user.user_permissions.add(Permission.objects.get(codename='add_worker'))
        worker = {
            'name': 'Ola Normann',
            'address': 'Adressegata 1, 0123 Oslo',
            'norlonn_number': '999',
        }
        first_post = self.client.post(reverse('worker-create', args=[self.society_name]), data=worker, follow=True)
        first_added_worker = Worker.objects.last()
        second_post = self.client.post(reverse('worker-create', args=[self.society_name]), data=worker, follow=True)
        self.assertEqual(first_added_worker, Worker.objects.last(),
                         "Worker created despite having a duplicate wage personnel number.")
        self.assertEqual(first_post.status_code, 200)
        self.assertEqual(second_post.status_code, 200)

    def test_create_worker_duplicate_national_id(self):
        """
        Tries to create a worker with a duplicate national ID.
        """
        self.user.user_permissions.add(Permission.objects.get(codename='add_worker'))
        worker = {
            'name': 'Ola Normann',
            'address': 'Adressegata 1, 0123 Oslo',
            'person_id': '01020332596',
        }
        first_post = self.client.post(reverse('worker-create', args=[self.society_name]), data=worker, follow=True)
        first_added_worker = Worker.objects.last()
        second_post = self.client.post(reverse('worker-create', args=[self.society_name]), data=worker, follow=True)
        second_added_worker = Worker.objects.last()
        self.assertEqual(first_added_worker, second_added_worker,
                         "Worker created despite having a duplicate national ID.")
        self.assertEqual(first_post.status_code, 200)
