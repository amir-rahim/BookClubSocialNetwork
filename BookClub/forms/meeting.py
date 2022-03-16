from django.forms import ModelForm, Textarea, TextInput, ValidationError

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
        
    def clean(self):
        super().clean()
        meeting_type = self.cleaned_data.get('type')
        if meeting_type == Meeting.MeetingType.BOOK:
            book = self.cleaned_data.get('book')
            if book is None:
                raise ValidationError("A book meeting needs a book selected!")
        
