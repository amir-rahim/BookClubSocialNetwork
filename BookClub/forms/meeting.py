from django.forms import HiddenInput, ModelForm, Textarea, TextInput, ValidationError
from BookClub.forms.widgets import BookSelectorInput,DateTimePickerInput
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
            'book' : BookSelectorInput(),
            'meeting_time': DateTimePickerInput
        }
        
    def clean(self):
        super().clean()
        meeting_type = self.cleaned_data.get('type')
        if meeting_type == Meeting.MeetingType.BOOK:
            book = self.cleaned_data.get('book')
            if book is None:
                self.add_error('book', "Book is required when creating a book meeting")
        
