from django import forms
from django.forms import ModelForm

from localflavor.no.forms import NOSocialSecurityNumber
from workers.models import Worker

class WorkerForm(ModelForm):
	person_id = NOSocialSecurityNumber(required=False)
	
	class Meta:
		model = Worker
		fields = ['name', 'address', 'account_no', 'person_id', 'norlonn_number' ]

class WorkerEditForm(ModelForm):
	person_id = NOSocialSecurityNumber(required=False)
	
	class Meta:
		model = Worker
		fields = ['name', 'address', 'account_no', 'person_id', 'norlonn_number', 'active' ]

