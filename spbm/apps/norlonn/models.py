from django.db import models
from django.utils.formats import localize
from django.utils.translation import ugettext_lazy as _


class NorlonnReport(models.Model):
    """
    Model for storing a report date, represented as a wage payout.

    That's... all.
    """

    class Meta:
        verbose_name = _("norlønn report")
        verbose_name_plural = _("norlønn reports")

    date = models.DateField()

    def __str__(self):
        return str(localize(self.date))

    class Meta:
        permissions = (
            ('generate_report', 'Can generate norlønn report'),
            ('view_report', 'Can view norlønn reports'),
        )
