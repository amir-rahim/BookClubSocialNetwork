from django.forms import ModelForm, Textarea
from django.test import tag
from BookClub.models.club import Club
from BookClub.models.user import User
from BookClub.models.meeting import Meeting


class MeetingForm(ModelForm):
    class Meta:
        model = Meeting
        fields = ['meeting_time', 'location', 'title', 'description', 'type',]

        widgets = {
            'description': Textarea,
        }

        