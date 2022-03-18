from django.forms import DateTimeInput, ModelForm, Textarea, TextInput
from BookClub.forms.widgets import DateTimePickerInput
from BookClub.models.meeting import Meeting


class MeetingForm(ModelForm):
    class Meta:
        model = Meeting
        fields = [
            'title',
            'description',
            'meeting_time',
            'location',
            'type',
            'book',
        ]

        widgets = {
            'description': Textarea,
            'meeting_time': DateTimePickerInput
        }
