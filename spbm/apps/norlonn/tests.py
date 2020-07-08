from django.test import TestCase
from django.contrib.auth.models import User, Permission
from django.urls import reverse

from ..society.tests import test_fixtures, SPFTestMixin, set_up_superuser, set_up_user
from ..accounts.models import SpfUser
from ..society.models import Invoice, Society, Event
from .models import NorlonnReport


class WageReportingTests(SPFTestMixin, TestCase):
    fixtures = test_fixtures

    @classmethod
    def setUpTestData(cls):
        set_up_user(cls, superuser=True)

    def setUp(self):
        self.client.force_login(self.user)

    def test_generate_report_with_get_does_nothing(self):
        """
        Generating a report using GET has no effect.
        """
        reports_before = NorlonnReport.objects.count()
        generating_report = self.client.get(reverse("wages-generate_report"))
        self.assertEqual(reports_before, NorlonnReport.objects.count())

    def test_generating_report_without_permissions(self):
        """
        Generating a report using POST without permission will fail.
        """
        reports_before = NorlonnReport.objects.count()
        generating_report = self.client.post(reverse("wages-generate_report"))
        self.assertEqual(reports_before, NorlonnReport.objects.count())
        self.assertEqual(generating_report.status_code, self.HTTP_FORBIDDEN)


class WageReportingNotReadyTests(SPFTestMixin, TestCase):
    fixtures = test_fixtures

    @classmethod
    def setUpTestData(cls):
        set_up_user(cls, superuser=True)

    def setUp(self):
        self.client.force_login(self.user)

    def test_generate_report_with_get_does_nothing(self):
        """
        Generating a report using GET has no effect.
        """
        reports_before = NorlonnReport.objects.count()
        generating_report = self.client.get(reverse("wages-generate_report"))
        self.assertEqual(reports_before, NorlonnReport.objects.count())

    def test_generating_report_without_permissions(self):
        """
        Generating a report using POST without permission will fail.
        """
        reports_before = NorlonnReport.objects.count()
        generating_report = self.client.post(reverse("wages-generate_report"))
        self.assertEqual(reports_before, NorlonnReport.objects.count())
        self.assertEqual(generating_report.status_code, self.HTTP_FORBIDDEN)
