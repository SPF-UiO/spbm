from django.contrib.auth.models import User, Permission
from django.test import TestCase
from django.urls import reverse

from . import test_fixtures, SPFTestMixin
from ..models import Invoice, Society, Event
from ...accounts.models import SpfUser


class InvoicingTests(SPFTestMixin, TestCase):
    fixtures = test_fixtures

    def setUp(self):
        # Logging into the site as a test in itself can be somewhere else. This doesn't need it.
        self.user = User(username='kungfury')
        self.user.save()
        self.spf_user = SpfUser(user=self.user, society=Society.objects.get(pk=2))
        self.spf_user.save()
        self.client.force_login(self.user)

    def test_get_all_invoices(self):
        """
        Return list of invoices to viewer.
        """
        response = self.client.get(reverse('invoices'))
        self.assertEqual(len(response.context['all_invoices']), len(Invoice.objects.all()))

    def test_view_an_invoice(self):
        """
        Show an invoice in HTML-style and PDF.
        """
        html_invoice = self.client.get(reverse('invoice-view', kwargs={'society_name': 'CYB', 'date': '2016-07-17'}))
        self.assertTrue(html_invoice.status_code, self.HTTP_OK)
        # Is there a mention of the SPF-fee?
        self.assertContains(html_invoice, "SPF")

    def test_get_unpaid_invoices(self):
        """
        Show unpaid invoices available for payment.
        Verify that the input field for marking as paid is there.
        """
        response = self.client.get(reverse('invoices'))
        body = response.content.decode()
        unpaid_invoices = Invoice.objects.filter(paid=False)
        self.assertInHTML("<input type='hidden' name='action' value='mark_paid'>", body,
                          count=len(unpaid_invoices))
        # Enumerate through each of the invoices and make sure that they're there!
        for unpaid in unpaid_invoices:
            self.assertInHTML("<input type='hidden' name='inv_id' value='{pk}'>".format(pk=unpaid.pk), body)

    def test_mark_invoice_as_paid_permitted(self):
        """
        Validate the ability to mark an invoice as paid.
        """
        # We can mark it, right?
        permission = Permission.objects.get(codename='mark_paid')
        self.user.user_permissions.add(permission)

        # Get an unpaid invoice
        unpaid_invoice = self.client.get(reverse('invoices')).context['unpaid_invoices'].first()
        self.assertEqual(unpaid_invoice.paid, False)

        marking_paid_response = self.client.post(reverse('invoicing'),
                                                 {'action': 'mark_paid',
                                                  'inv_id': unpaid_invoice.pk})
        # Need to refresh from the database!
        unpaid_invoice.refresh_from_db()

        # Is the invoice paid?
        self.assertEqual(unpaid_invoice.paid, True)
        # Do we get redirected?
        self.assertEqual(marking_paid_response.status_code, self.HTTP_FOUND)

    def test_mark_invoice_as_paid_denied(self):
        """
        Validate being unable to mark an invoice as paid without the permission.
        """
        marking_paid_response = self.client.post(reverse('invoicing'),
                                                 {'action': 'mark_paid',
                                                  'inv_id': 2})
        self.assertEqual(Invoice.objects.get(pk=2).paid, False)
        self.assertEqual(marking_paid_response.status_code, self.HTTP_FORBIDDEN)

    def test_unprocessed_events_count(self):
        """
        Validate that the count for unprocessed events is correct.
        Depends on fixtures or setup data being correct.
        """
        response_number = self.client.get(reverse('invoices')).context['unprocessed_events']
        self.assertNotEqual(response_number, 0)

    def test_close_period_permitted(self):
        """
        Validate being able to close a period with the given permission.
        """
        self.user.user_permissions.add(Permission.objects.get(codename='close_period'))

        # Make sure that we've actually
        self.assertNotEqual(self.client.get(reverse('invoices')).context['unprocessed_events'],
                            0)

        closed_period = self.client.post(reverse('invoicing'),
                                         {'action': 'close_period'})

        listing = self.client.get(reverse('invoices'))

        self.assertEqual(listing.context['unprocessed_events'], 0)
        self.assertEqual(closed_period.status_code, self.HTTP_FOUND)

    def test_close_period_denied(self):
        """
        Validate being unable to close a period without the permission.
        """
        closed_period = self.client.post(reverse('invoicing'),
                                         {'action': 'close_period'})

        self.assertEqual(closed_period.status_code, self.HTTP_FORBIDDEN)

    def test_close_period_twice_in_a_day_fail(self):
        """
        Periods shouldn't be possible to close twice in a day for an invoiced society.
        Test for messages.
        """
        self.user.user_permissions.add(Permission.objects.get(codename='close_period'))
        # Create an event, contents unimportant, then close period
        Event.objects.create(date="2000-01-01", society=self.spf_user.society)
        self.client.post(reverse('invoicing'), {'action': 'close_period'}, follow=True)

        # Create an event, contents unimportant, then close period again
        Event.objects.create(date="2000-01-01", society=self.spf_user.society)
        second_period = self.client.post(reverse('invoicing'), {'action': 'close_period'}, follow=True)

        self.assertEqual(len(second_period.context['messages']), 1)
        self.assertMessagesContains(second_period, "cannot close a period twice")
        self.assertContains(second_period, "cannot close")
