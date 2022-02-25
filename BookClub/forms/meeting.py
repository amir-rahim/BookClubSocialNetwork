from django import forms
from django.forms import ModelForm, Textarea, TextInput
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
            'meeting_time': TextInput(attrs={'placeholder': 'YYYY/MM/DD HH:MM:SS'})
        }
