from django.contrib.auth.models import User, Permission
from django.http import HttpResponse, HttpResponseRedirect
from django.test import TestCase
from django.urls import reverse

from spbm.apps.accounts.models import SpfUser
from spbm.apps.norlonn.models import NorlonnReport
from spbm.apps.society.models import Society, Worker
from . import test_fixtures, SPFTestMixin


class WagesTests(SPFTestMixin, TestCase):
    fixtures = test_fixtures

    @classmethod
    def setUpTestData(cls):
        cls.society_name = 'CYB'
        cls.existing_report = '2016-07-17'
        cls.society = Society.objects.get(shortname=cls.society_name)

    def setUp(self):
        self.user = User()
        self.user.save()
        self.spf_user = SpfUser(user=self.user, society=Society.objects.get(shortname=self.society_name))
        self.spf_user.save()
        self.client.force_login(self.user)

    def test_wage_views(self):
        """
        Checks access to views and that they barebones work.
        """
        tests = [['wages-export_report', [self.existing_report], 'export_report'],
                 ['wages-generate_report', [], 'generate_report']]

        for test in tests:
            with self.subTest("testing {view}".format(view=test[0])):
                # Confirm that permissions stop us
                failed_response = self.client.post(reverse(test[0], args=test[1]))
                self.assertEqual(failed_response.status_code, self.HTTP_FORBIDDEN)
                # Confirm that adding permissions actually works
                self.user.user_permissions.add(Permission.objects.get(codename=test[2]))
                export_response = self.client.post(reverse(test[0], args=test[1]))
                self.assertEqual(export_response.status_code, self.HTTP_OK)

    def test_generate_report_no_get(self):
        """ Verify that attempting to GET does not create a report """
        self.user.user_permissions.add(Permission.objects.get(codename='generate_report'))
        self.assertIsInstance(self.client.get(reverse('wages-generate_report')), HttpResponseRedirect)
        self.assertTrue(NorlonnReport.objects.count() == 1, "Report was generated")

    def test_generate_and_export_report(self):
        """
        Test generation of report and that it yields correct output together with exporting.
        """
        current_report = NorlonnReport.objects.first()
        self.user.user_permissions.add(Permission.objects.get(codename='export_report'))
        report_response = self.client.get(reverse('wages-export_report', args=[self.existing_report]))
        self.assertEqual(report_response.content, bytes(";101;H1;100;390000;", encoding='utf8'))
        self.assertEqual(report_response.status_code, self.HTTP_OK)

        # Generate the new one
        self.user.user_permissions.add(Permission.objects.get(codename='generate_report'))
        generate_response = self.client.post(reverse('wages-generate_report'))
        self.assertTemplateUsed(generate_response, 'norlonn/report.jinja')

        new_report = NorlonnReport.objects.last()
        self.assertNotEqual(current_report, new_report, "Report was not generated")
        export_new = self.client.get(reverse('wages-export_report', args=[NorlonnReport.objects.last().date]))
        self.assertEqual(export_new.content, bytes(";101;H1;100;234000;", encoding='utf8'))

        # Can we generate a new one right afterwards? No, because there's no new payrolls we can do anything with
        no_valid = self.client.post(reverse('wages-generate_report'), follow=True)
        self.assertEqual(new_report, NorlonnReport.objects.last())
        self.assertMessagesContains(no_valid, "no valid shifts that can be added")

        # Even if we fix something, we can't because it's the same date
        lucky_james = Worker.objects.get(pk=2)
        lucky_james.norlonn_number = 1337
        lucky_james.save()
        same_date = self.client.post(reverse('wages-generate_report'), follow=True)
        self.assertMessagesContains(same_date, "payroll already exists")



