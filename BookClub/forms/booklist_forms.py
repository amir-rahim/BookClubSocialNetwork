from django import forms
from django.forms import ModelForm, Textarea, Form
from numpy import require

from BookClub.models import BookList


class CreateBookListForm(ModelForm):
    class Meta:
        model = BookList
        fields = ['title', 'description']

        widgets = {
            'description': Textarea,
        }


class AddBookForm(Form):
    book = forms.IntegerField(required=True)
    booklist = forms.IntegerField(required=True)
