from django.contrib.auth.models import User
from django.utils.translation import ugettext, ugettext_lazy as _
from django.db import models


class SpfUser(models.Model):
    class Meta:
        verbose_name = _('SPF-user')
        verbose_name_plural = _('SPF-users')

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    society = models.ForeignKey('society.Society', verbose_name=_('Society'), null=True, on_delete=models.SET_NULL,
                                help_text=_('The society within SPF that the user has as a primary connection.'))

    def __str__(self):
        return ugettext("SPF-member connected to {society}".format(society=self.society))
