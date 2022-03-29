from django import forms
from django.forms import HiddenInput, ModelForm, Textarea

from BookClub.models import Club, FeaturedBooks
from BookClub.forms.widgets import BookSelectorInput


class ClubForm(ModelForm):
    class Meta:
        model = Club
        fields = ['name', 'description', 'tagline', 'rules', 'is_private']

        widgets = {
            'description': Textarea,
        }

        labels = {
            'is_private': 'Set book club as private'
        }

class FeatureBookForm(ModelForm):
    class Meta:
        model = FeaturedBooks
        fields = ['book','reason']
        widgets = {
            'book' : BookSelectorInput(),
            'reason' : forms.TextInput(attrs={'placeholder': 'Optional'})
        }
        
    def clean(self):
        super().clean()
        book = self.cleaned_data.get('book')
        if book is None:
            self.add_error('book', "Book is required")
