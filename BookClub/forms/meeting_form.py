from django.forms import CheckboxSelectMultiple, DateTimeInput, ModelForm, SelectDateWidget, SelectMultiple, SplitDateTimeWidget, Textarea
from django.test import tag
from BookClub.models.club import Club
from BookClub.models.user import User
from BookClub.models.meeting import Meeting


class MeetingForm(ModelForm):
    class Meta:
        model = Meeting
        fields = ['title', 'description','location','meeting_time', 'type']

        widgets = {
            'description': Textarea,
            'meeting_time': DateTimeInput
        }

        