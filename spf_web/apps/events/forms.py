from django.forms import ModelChoiceField, DecimalField, DateInput
from django.forms import ModelForm, Form

from spf_web.apps.events.models import Event
from spf_web.apps.society.models import Worker


class MyDateInput(DateInput):
    input_type = 'date'


class EventForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
        self.fields['date'].widget = MyDateInput(attrs={'class': 'date'})

    class Meta:
        model = Event
        fields = ['name', 'date']


def MakeShiftBase(society):
    class ShiftForm(Form):
        def __init__(self, *args, **kwargs):
            super(ShiftForm, self).__init__(*args, initial={'wage': society.default_wage}, **kwargs)
            self.fields['worker'].queryset = Worker.objects.filter(society=society, active=1)

        worker = ModelChoiceField(queryset=Worker.objects.filter(society=society))
        wage = DecimalField(max_digits=10, decimal_places=2)
        hours = DecimalField(max_digits=10, decimal_places=2)

    return ShiftForm
