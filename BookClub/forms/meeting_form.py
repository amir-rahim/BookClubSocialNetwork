from django.forms import DateTimeInput, ModelForm, Textarea

from BookClub.models import Meeting


class MeetingForm(ModelForm):
    class Meta:
        model = Meeting
        fields = ['title', 'description', 'location', 'meeting_time', 'type']

        widgets = {
            'description': Textarea,
            'meeting_time': DateTimeInput
        }
