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
            'meeting_end_time',
            'location',
            'type',
            'book',
        ]

        widgets = {
            'description': Textarea,
            'book' : BookSelectorInput(),
            'meeting_time': DateTimePickerInput,
            'meeting_end_time': DateTimePickerInput
        }
        
    def clean(self):
        super().clean()
        meeting_type = self.cleaned_data.get('type')
        meeting_time = self.cleaned_data.get('meeting_time')
        meeting_end_time = self.cleaned_data.get('meeting_end_time')
        if meeting_type == Meeting.MeetingType.BOOK:
            book = self.cleaned_data.get('book')
            if book is None:
                self.add_error('book', "Book is required when creating a book meeting")

            if meeting_time > meeting_end_time:
                self.add_error('meeting_end_time', 'Meeting end time must be after the meeting time.')
