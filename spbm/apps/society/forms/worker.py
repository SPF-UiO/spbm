from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _
from localflavor.no.forms import NOSocialSecurityNumber

from ..models import Worker


class WorkerForm(ModelForm):
    """
    Form for creating a new worker.
    """
    # This overwrites the meta definition.
    person_id = NOSocialSecurityNumber(required=False,
                                       label=_('National ID'),
                                       help_text=_('National social security ID, 11 digits.'))

    class Meta:
        model = Worker
        fields = ['name', 'address', 'account_no', 'person_id', 'norlonn_number']


class WorkerEditForm(WorkerForm):
    """
    Form for editing an already existing worker.
    """

    class Meta(WorkerForm.Meta):
        fields = ['name', 'address', 'account_no', 'person_id', 'norlonn_number', 'active']
