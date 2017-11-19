from django.forms import ModelForm, Form
from django.utils.translation import ugettext_lazy as _
from localflavor.no.forms import NOSocialSecurityNumber, NOBankAccountNumber

from ..models import Worker


def person_id(**kwargs):
    return NOSocialSecurityNumber(label=_('National ID'),
                                  help_text=_('National social security ID, 11 digits.'),
                                  **kwargs)

def account_no(**kwargs):
    return NOBankAccountNumber(label=_('Bank account'),
                                  help_text=_('Bank account number, 11 digits.'),
                                  **kwargs)

class WorkerForm(ModelForm):
    """
    Form for creating a new worker.
    """
    # This overwrites the meta definition.
    person_id = person_id(required=False)
    account_no = account_no(required=False)

    class Meta:
        model = Worker
        fields = ['name', 'address', 'account_no', 'person_id', 'norlonn_number']


class WorkerPersonIDForm(Form):
    """
    Form for dealing with workers person IDs, such as looking up by them.
    """
    person_id = person_id(required=True)


class WorkerEditForm(WorkerForm):
    """
    Form for editing an already existing worker.
    """

    class Meta(WorkerForm.Meta):
        fields = ['name', 'address', 'account_no', 'person_id', 'norlonn_number']
