from decimal import Decimal

from django.contrib.auth.models import User, AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import six
from django.utils.functional import lazy
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

mark_safe_lazy = lazy(mark_safe, six.text_type)


class Society(models.Model):
    """
    Model for student societies -- and other members -- of SPF.
    """

    class Meta:
        verbose_name = _('society')
        verbose_name_plural = _('societies')

    name = models.CharField(max_length=100,
                            verbose_name=_('name'))
    shortname = models.CharField(max_length=10,
                                 verbose_name=_('abbreviated name'))
    invoice_email = models.EmailField(default="",
                                      verbose_name=_('invoice e-mail'))
    default_wage = models.DecimalField(max_digits=10, decimal_places=2,
                                       verbose_name=_('default wage per hour'))
    logo = models.FileField(null=True, blank=True, verbose_name=_('logo'))

    def __str__(self):
        return self.shortname


class Worker(models.Model):
    """
    Model for student -- and other types of -- workers.
    """

    class Meta:
        verbose_name = _('worker')
        verbose_name_plural = _('workers')

    class WorkerManager(models.Manager):
        def get_queryset(self):
            return super().get_queryset().select_related('society')


    societies = models.ManyToManyField(Society,
                                       through='Employment',
                                       related_name='workers')
    active = models.BooleanField(default=True,
                                 verbose_name=_('active'),
                                 help_text=_('Check off if the worker is still actively working.'))
    name = models.CharField(max_length=1000,
                            verbose_name=_('name'),
                            help_text=_('Full name, with first name first.'))
    address = models.CharField(max_length=1000,
                               verbose_name=_('address'),
                               help_text=_('Full address including postal code and area.'))
    account_no = models.CharField(max_length=20,
                                  blank=True,
                                  verbose_name=_('account no.'),
                                  help_text=_('Norwegian bank account number, no periods, 11 digits.'))
    person_id = models.CharField(max_length=20,
                                 blank=True,
                                 verbose_name=_('person ID'))
    norlonn_number = models.IntegerField(blank=True,
                                         null=True,
                                         unique=True,
                                         verbose_name=_("norl&oslash;nn number"),
                                         help_text=mark_safe_lazy(_(
                                             "Employee number in the wage system, Norl&oslash;nn. " +
                                             "<strong>Must</strong> exist and be correct!")))

    objects = WorkerManager()

    def __str__(self):
        return self.name + " (" + self.society.shortname + ")"

class Employment(models.Model):
    """
    Through-model for the relationship between a worker and a society.
    :keyword !Society
    :keyword !Worker
    """

    class Meta:
        unique_together = ('worker', 'society')

    worker = models.ForeignKey(Worker,
                               on_delete=models.CASCADE)
    society = models.ForeignKey(Society,
                                on_delete=models.PROTECT)
    active = models.BooleanField(default=True, null=False)


class Invoice(models.Model):
    """
    Model for the invoices associated with closing a period of events.
    """

    class Meta:
        verbose_name = _('invoice')
        verbose_name_plural = _('invoices')
        unique_together = ('period', 'society')
        permissions = (
            ('close_period', "Can close periods to generate invoices"),
            ('mark_paid', "Can mark invoices as paid")
        )

    """ The society the invoice belongs to. """
    society = models.ForeignKey(Society, verbose_name=_('society'), related_name="invoices", on_delete=models.PROTECT)
    """ A unique invoice number, which SHOULD be reflected in the external invoice system. """
    invoice_number = models.IntegerField(verbose_name=_('invoice number'), unique=True)
    """ The date for which the period is valid. """
    period = models.DateField(verbose_name=_('period'))
    """ Status of received payment. """
    paid = models.BooleanField(verbose_name=_('invoice paid'), default=False)
    """ User who created the invoice, i.e. closed the invoice period. """
    created_by = models.ForeignKey(User, help_text=_('User which closed the period the invoice belongs to.'),
                                   on_delete=models.PROTECT, null=True, default=None)

    def get_total_cost(self):
        """
        Calculates the cost for an event, including the percentage fee.
        :return: Decimal of total event cost, including the fee.
        """
        cost = 0
        events = Event.objects.filter(invoice=self)

        for event in events:
            cost += event.cost

        return (Decimal(cost) * Decimal('1.3')).quantize(Decimal('.01'))

    def get_total_event_cost(self):
        """
        Calculates the cost for the invoice in regards to the events alone.
        :return: Decimal of total event cost, not including the fee.
        """
        cost = 0
        events = Event.objects.filter(invoice=self)
        for event in events:
            cost += event.cost

        return Decimal(cost).quantize(Decimal('.01'))

    def __str__(self):
        return "Invoice #{id}: {period} {society} ".format(id=str(self.invoice_number),
                                                           society=str(self.invoice_number), period=str(self.period))


class Event(models.Model):
    """
    Model for events, bookings and other sorts of works performed by societies.
    """

    class Meta:
        verbose_name = _('event')
        verbose_name_plural = _('events')

    class EventManager(models.Manager):
        def get_queryset(self):
            return super().get_queryset().prefetch_related('shifts__worker', 'society')

    society = models.ForeignKey(Society, null=False, verbose_name=_('society'), related_name="society",
                                on_delete=models.PROTECT)
    name = models.CharField(max_length=100,
                            verbose_name=_('name'),
                            help_text=_('Name or title describing the event.'))
    date = models.DateField(verbose_name=_('event date'),
                            help_text=_('The date of the event in the format of <em>YYYY-MM-DD</em>.'))
    registered = models.DateField(auto_now_add=True,
                                  editable=False,
                                  verbose_name=_('registered'),
                                  help_text=_('Date of event registration.'))
    ''' 'processed' and 'invoice' are very tightly coupled together.
    Why exactly are both needed? Any invoice is processed on an exact date. If it shouldn't be part of an invoice,
    then it is not really processed anyway. '''
    # TODO: Create migration from processed to purely invoice, alt. from field to property method.
    processed = models.DateField(null=True,
                                 blank=True,
                                 verbose_name=_('processed'))
    # If you've got an invoice, maybe it shouldn't be allowed to be deleted.
    # However, do we have some other good ways of doing it? :/ I mean, *easy* ways of doing it?
    # Let's be difficult with ourselves. Don't delete the invoices, just remove the invoice from the event!
    invoice = models.ForeignKey(Invoice,
                                null=True,
                                blank=True,
                                on_delete=models.PROTECT,
                                related_name="events",
                                verbose_name=_('invoice'))

    objects = EventManager()

    @property
    def hours(self):
        """ Get the number of hours registered on an event """
        hours = Decimal(0)
        for shift in self.shifts.all():
            hours += shift.hours
        hours = hours.quantize(Decimal(".01"))
        return hours

    hours.fget.short_description = _("Total hours")

    @property
    def cost(self):
        """ Get the total cost that will be invoiced from an event """
        total = Decimal(0)
        for s in self.shifts.all():
            total += s.get_total()
        total = total.quantize(Decimal(".01"))
        return total

    cost.fget.short_description = _("Total cost")

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('event-view', args=[self.pk])

    def clean(self):
        if self.invoice is not None:
            if self.invoice.society != self.society:
                raise ValidationError("Cannot add event to another society invoice!")

    def __str__(self):
        return self.society.shortname + " - " + str(self.date) + ": " + self.name


class Shift(models.Model):
    """
    Model for a worker's shift during an event.
    """

    class Meta:
        verbose_name = _('shift')
        verbose_name_plural = _('shifts')
        unique_together = ("event", "worker")

    event = models.ForeignKey(Event, related_name="shifts", on_delete=models.CASCADE)
    worker = models.ForeignKey(Worker,
                               on_delete=models.PROTECT,
                               related_name="shifts",
                               verbose_name=_('worker'))
    wage = models.DecimalField(max_digits=10,
                               decimal_places=2,
                               verbose_name=_('wage'),
                               validators=[MinValueValidator(10)])
    hours = models.DecimalField(max_digits=10,
                                decimal_places=2,
                                verbose_name=_('hours'),
                                validators=[MinValueValidator(0.25)])
    norlonn_report = models.ForeignKey('norlonn.NorlonnReport',
                                       blank=True,
                                       null=True,
                                       on_delete=models.SET_NULL,
                                       related_name="shifts",
                                       verbose_name=_('norl&oslash;nn report'))

    norlonn_report.short_description = "Sent to norlønn"

    def clean(self):
        """ Cleans the shift, making sure it isn't attached to a worker not part of the society """
        try:
            if self.event.society not in self.worker.societies.all():
                raise ValidationError(_('Worker on shift does not belong to the same society as the event.'))
        except:
            raise ValidationError(_('You must select a worker for this shift.'))

    def get_total(self):
        return (self.wage * self.hours).quantize(Decimal(".01"))
