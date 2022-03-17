from django.forms import HiddenInput, ModelForm, Textarea, TextInput, ValidationError
from BookClub.forms.widgets import BookSelectorInput

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
            'meeting_time': TextInput(attrs={'placeholder': 'YYYY/MM/DD HH:MM:SS'}),
            'book' : BookSelectorInput()
            
        }
        
    def clean(self):
        super().clean()
        meeting_type = self.cleaned_data.get('type')
        if meeting_type == Meeting.MeetingType.BOOK:
            book = self.cleaned_data.get('book')
            if book is None:
                self.add_error('book', "Book is required when creating a book meeting")
        
