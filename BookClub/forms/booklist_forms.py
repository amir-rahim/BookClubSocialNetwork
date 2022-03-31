"""Book list related forms."""
from django import forms
from django.forms import ModelForm, Textarea, Form
from numpy import require

from BookClub.models import BookList


class CreateBookListForm(ModelForm):
    """Form for the user to create a new book list"""
    class Meta:
        model = BookList
        fields = ['title', 'description']

        widgets = {
            'description': Textarea,
        }


class AddBookForm(Form):
    """Allows user to add a book to their book list."""
    book = forms.IntegerField(required=True)
    booklist = forms.IntegerField(required=True)
