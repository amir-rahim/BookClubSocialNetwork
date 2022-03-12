from django.forms import ModelForm, Textarea, ValidationError, Form
from django import forms
from django.core.validators import RegexValidator
from BookClub.models import BookList

class CreateBookListForm(ModelForm):
    class Meta:
        model = BookList
        fields = ['title', 'description']

        widgets = {
            'description': Textarea,
        }

class AddBookForm(Form):
    book = forms.IntegerField()
    booklist = forms.IntegerField()