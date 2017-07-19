from django import forms

from spbm.apps.society.models import Worker, Event, Shift


class DateInput(forms.DateInput):
    input_type = 'date'


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['name', 'date']
        widgets = {
            'date': DateInput(attrs={'class': 'date'})
        }


def make_shift_base(society):
    """ Takes a society and returns a Shift form with initial data populated based of society defaults """

    class ShiftForm(forms.ModelForm):
        class Meta:
            model = Shift
            exclude = ['norlonn_report']
            widgets = {
                'wage': forms.NumberInput(attrs={'step': 1}),
                'hours': forms.NumberInput(attrs={'step': '0.25'})
            }

        def __init__(self, *args, **kwargs):
            super(ShiftForm, self).__init__(*args, initial={'wage': society.default_wage}, **kwargs)
            self.fields['worker'].queryset = Worker.objects.filter(society=society, active=True)

    return ShiftForm




