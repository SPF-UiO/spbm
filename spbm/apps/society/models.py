from decimal import Decimal

from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Sum, F
from django.urls import reverse
from django.utils import six
from django.utils.functional import lazy
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _, ugettext

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
                                       default=Decimal("160"), verbose_name=_('default wage per hour'))
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

    societies = models.ManyToManyField(Society,
                                       through='Employment',
                                       related_name='workers')
    name = models.CharField(max_length=1000,
                            verbose_name=_('name'),
                            help_text=_('Full name, with first name first.'))
    address = models.CharField(max_length=1000,
                               verbose_name=_('address'),
                               help_text=_('Full address including postal code and area.'))
    account_no = models.CharField(max_length=20,
                                  blank=True,
                                  null=True,
                                  verbose_name=_('account no.'),
                                  help_text=_('Norwegian bank account number, no periods, 11 digits.'))
    person_id = models.CharField(max_length=20,
                                 blank=True,
                                 null=True,
                                 unique=True,
                                 verbose_name=_('person ID'))
    norlonn_number = models.IntegerField(blank=True,
                                         null=True,
                                         unique=True,
                                         verbose_name=_("norl&oslash;nn number"),
                                         help_text=mark_safe_lazy(_(
                                             "Employee number in the wage system, Norl&oslash;nn. " +
                                             "<strong>Must</strong> exist and be correct!")))

    def get_absolute_url(self):
        return reverse('worker-view', args=[str(self.id)])

    def __str__(self):
        return self.name + " (#" + str(self.id) + ")"


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
    active = models.BooleanField(default=True, null=False, verbose_name=_('active'),
                                 help_text=_('Check off if the worker is still actively working.'))


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

    class InvoiceManager(models.Manager):
        def get_queryset(self):
            """ select_related() to improve performance """
            return super().get_queryset().select_related()

    """ The society the invoice belongs to """
    society = models.ForeignKey(Society, verbose_name=_('society'), related_name="invoices", on_delete=models.PROTECT)
    """ A unique invoice number, which SHOULD be reflected in the external invoice system """
    invoice_number = models.IntegerField(verbose_name=_('invoice number'), unique=True)
    """ The date for which the period is valid """
    period = models.DateField(verbose_name=_('period'))
    """ Status of received payment """
    paid = models.BooleanField(verbose_name=_('invoice paid'), default=False)
    """ User who created the invoice, i.e. closed the invoice period """
    created_by = models.ForeignKey(User, help_text=_('User which closed the period the invoice belongs to.'),
                                   on_delete=models.PROTECT, null=True, default=None)

    objects = InvoiceManager()

    def get_total_cost(self):
        """
        Calculates the cost for an event, including the percentage fee.
        :return: Decimal of total event cost, including the fee.
        """
        # FIXME: Decimal issues: should we add output_field=models.FloatField?
        total_costs = Decimal(
            self.events.all()
                .aggregate(total_cost=Sum('sum_costs'))
                .get('total_cost'))

        fee = self.get_fee_cost(total_costs)

        return (total_costs + fee).quantize(Decimal('.01'))

    def get_total_event_cost(self):
        """
        Calculates the cost for the invoice in regards to the events alone.
        :return: Decimal of total event cost, not including the fee.
        """
        total_event_costs = Decimal(
            self.events.all()
                .aggregate(total_event_cost=Sum('sum_costs'))
                .get('total_event_cost'))

        return total_event_costs.quantize(Decimal('.01'))

    @classmethod
    def get_fee_cost(cls, event_total_cost):
        return (Decimal(event_total_cost) * Decimal(settings.SPBM.get('fee'))).quantize(Decimal('.01'))

    def __str__(self):
        return ugettext("Invoice #{id}: {period} {society}").format(id=str(self.invoice_number),
                                                                    society=str(self.society.shortname),
                                                                    period=str(self.period))


class Event(models.Model):
    """
    Model for events, bookings and other sorts of works performed by societies.
    """

    class Meta:
        verbose_name = _('event')
        verbose_name_plural = _('events')

    class EventManager(models.Manager):
        def get_queryset(self):
            """ Changed manager to include sum of costs and hours, plus related society by default """
            return (super().get_queryset().select_related()
                    .prefetch_related('shifts__worker')
                    .annotate(sum_costs=Sum(F('shifts__hours') * F('shifts__wage'),
                                            output_field=models.DecimalField(decimal_places=2)),
                              sum_hours=Sum('shifts__hours',
                                            output_field=models.DecimalField(decimal_places=2))))

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
        """ Dynamically get the number of hours registered on an event """
        hours = Decimal(0)
        for shift in self.shifts.all():
            hours += shift.hours
        hours = hours.quantize(Decimal(".01"))
        return hours

    hours.fget.short_description = _("Total hours")

    @property
    def cost(self):
        """ Dynamically get the total cost that will be invoiced from an event """
        cost = Decimal(0)
        for shift in self.shifts.all():
            cost += (shift.hours * shift.wage)
        cost = cost.quantize(Decimal(".01"))
        return cost

    cost.fget.short_description = _("Total cost")

    def clean(self):
        if self.invoice is not None:
            if self.invoice.society != self.society:
                raise ValidationError("Cannot add event to another society invoice!")

    def get_absolute_url(self):
        return reverse('event-view', args=[self.id])

    def __str__(self):
        return "{short_name} - {date}: {name}".format(short_name=self.society.shortname,
                                                      date=self.date,
                                                      name=self.name)


class Shift(models.Model):
    """
    Model for a worker's shift during an event.
    """

    class Meta:
        verbose_name = _('shift')
        verbose_name_plural = _('shifts')
        unique_together = ("event", "worker")

    class ShiftManager(models.Manager):
        def get_queryset(self):
            """ Changed default manager to select related event's society and report """
            return super().get_queryset().select_related('event__society', 'norlonn_report')

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

    objects = ShiftManager()

    def clean(self):
        """ Cleans the shift, making sure it isn't attached to a worker not part of the society """
        try:
            if self.event.society not in self.worker.societies.all():
                raise ValidationError(_('Worker on shift does not belong to the same society as the event.'))
        except:
            raise ValidationError(_('You must select a worker for this shift.'))

    def get_total(self):
        return (self.wage * self.hours).quantize(Decimal(".01"))

    def get_absolute_url(self):
        return self.event.get_absolute_url()
