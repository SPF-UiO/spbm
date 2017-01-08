from django.conf import settings
from django.contrib.auth.models import User, Permission
from django.core.urlresolvers import reverse
from django.test import TestCase

from . import test_fixtures
from ..models import Invoice, Society
from ...accounts.models import SpfUser


class InvoicingTests(TestCase):
    fixtures = test_fixtures

    def setUp(self):
        # Turn on the django-jinja template debug to provide response.context in the client.
        # NOTE: Do *not* change any other settings on-the-fly. This one only affects this exact issue,
        #       and as such it's safe to edit. Otherwise Django settings are _immutable_.
        settings.TEMPLATES[0]['OPTIONS']['debug'] = True

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
        response = self.client.get(reverse('invoices-list'))
        self.assertEquals(len(response.context['invoices']), len(Invoice.objects.all()))

    def test_get_unpaid_invoices(self):
        """
        Show unpaid invoices available for payment.
        Verify that the input field for marking as paid is there.
        """
        response = self.client.get(reverse('invoices-all'))
        body = response.content.decode()
        unpaid_invoices = Invoice.objects.filter(paid='')
        self.assertInHTML("<input type='hidden' name='action' value='mark_paid'>", body,
                          count=len(unpaid_invoices))
        for unpaid in unpaid_invoices:
            self.assertInHTML("<input type='hidden' name='inv_id' value='{pk}'>".format(pk=unpaid.pk), body)

    def test_mark_invoice_as_paid_permitted(self):
        """
        Validate the ability to mark an invoice as paid.
        """
        # We can mark it, right?
        permission = Permission.objects.get(codename='mark_paid')
        self.user.user_permissions.add(permission)
        self.assertEquals(permission, self.user.user_permissions.get(codename='mark_paid'))

        # Get an unpaid invoice
        unpaid_invoice = self.client.get(reverse('invoices-all')).context['invoices'].first()
        self.assertEquals(unpaid_invoice.paid, False)

        marking_paid_response = self.client.post(reverse('invoices-all'),
                                                 {'action': 'mark_paid',
                                                  'inv_id': unpaid_invoice.pk})

        # Is the invoice paid?
        self.assertEquals(unpaid_invoice.paid, True)
        # Do we get redirected?
        self.assertEquals(marking_paid_response.status_code, 302)

    def test_mark_invoice_as_paid_denied(self):
        """
        Validate being unable to mark an invoice as paid without the permission.
        """
        marking_paid_response = self.client.post(reverse('invoices-all'),
                                                 {'action': 'mark_paid',
                                                  'inv_id': 2})
        self.assertEquals(Invoice.objects.get(pk=2).paid, False)
        self.assertEquals(marking_paid_response.status_code, 403)

    def test_close_period_permitted(self):
        """
        Validate being able to close a period with the given permission.
        """
        self.user.user_permissions.add(Permission.objects.get(codename='close_period'))

        closed_period = self.client.post(reverse('invoices-all'),
                                         {'action': 'close_period'})

        listing = self.client.get(reverse('invoices-all'))

        self.assertEquals(listing.context['unprocessed_events'], 0)
        self.assertEquals(closed_period.status_code, 302)

    def test_close_peried_denied(self):
        """
        Validate being unable to close a period without the permission.
        """
        closed_period = self.client.post(reverse('invoices-all'),
                                         {'action': 'close_period'})

        self.assertEquals(closed_period.status_code, 403)
