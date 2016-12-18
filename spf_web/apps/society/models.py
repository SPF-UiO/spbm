from django.db import models

from django.utils import six
from django.utils.functional import lazy
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

mark_safe_lazy = lazy(mark_safe, six.text_type)


class Society(models.Model):
    name = models.CharField(max_length=100)
    shortname = models.CharField(max_length=10)
    invoice_email = models.EmailField(default="")
    default_wage = models.DecimalField(max_digits=10, decimal_places=2)
    logo = models.FileField(null=True)

    def __str__(self):
        return self.shortname


class Worker(models.Model):
    """
    Model for student -- and other types of -- workers.
    """
    society = models.ForeignKey(Society, on_delete=models.PROTECT, related_name="workers")
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
                                 blank=True)
    norlonn_number = models.IntegerField(blank=True,
                                         null=True,
                                         unique=True,
                                         verbose_name=_("norl&oslash;nn number"),
                                         help_text=mark_safe_lazy(_(
                                             "Employee number in the wage system, Norl&oslash;nn. " +
                                             "<strong>Must</strong> exist and be correct!")))

    def __str__(self):
        return self.name + " (" + self.society.shortname + ")"
