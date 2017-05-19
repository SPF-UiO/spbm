from django.forms import DateInput
from django.forms import ModelForm

from spbm.apps.society.models import Worker, Event, Shift


class MyDateInput(DateInput):
    input_type = 'date'


class EventForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
        self.fields['date'].widget = MyDateInput(attrs={'class': 'date'})

    class Meta:
        model = Event
        fields = ['name', 'date']


def make_shift_base(society):
    """ Takes a society and returns a Shift form with initial data populated based of society defaults """

    class ShiftForm(ModelForm):
        class Meta:
            model = Shift
            exclude = ['norlonn_report']

        def __init__(self, *args, **kwargs):
            super(ShiftForm, self).__init__(*args, initial={'wage': society.default_wage}, **kwargs)
            self.fields['worker'].queryset = Worker.objects.filter(society=society, active=True)

    return ShiftForm




