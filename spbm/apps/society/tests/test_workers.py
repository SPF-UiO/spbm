from django.contrib.auth.models import User, Permission
from django.test import TestCase
from django.urls import reverse

from spbm.apps.accounts.models import SpfUser
from spbm.apps.society.models import Society, Worker
from . import test_fixtures


class WorkerTests(TestCase):
    fixtures = test_fixtures

    def setUp(self):
        # Logging into the site as a test in itself can be somewhere else. This doesn't need it.
        self.user = User(username='cyb')
        self.user.save()
        self.spf_user = SpfUser(user=self.user, society=Society.objects.get(pk=2))
        self.spf_user.save()
        self.client.force_login(self.user)

    @classmethod
    def setUpTestData(cls):
        cls.test = True
        cls.society_name = 'CYB'

    def test_create_worker(self):
        # TODO: finish test
        worker = {
            'name': 'Ola Normann',
            'norlonn_number': '100',
            'person_id': '01020394311',

        }
        self.assertEqual(self.client.post(reverse('worker-create', args=[self.society_name]), data=worker).status_code,
                         403)
        self.user.user_permissions.add(Permission.objects.get(codename='add_worker'))
        last_worker = Worker.objects.last()
        post = self.client.post(reverse('worker-create', args=[self.society_name]), data=worker)
        self.assertNotEqual(last_worker, Worker.objects.last())
        self.assertEqual(post.status_code, 200)

    def test_create_worker_duplicate_norlonn(self):
        pass

    def test_create_worker_duplicate_national_id(self):
        pass
