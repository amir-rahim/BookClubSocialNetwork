from django.forms import ModelForm, Textarea, ValidationError
from django.core.validators import RegexValidator
from django.test import tag
from BookClub.models import BookList

class CreateBookListForm(ModelForm):
    class Meta:
        model = BookList
        fields = ['title', 'description']

        widgets = {
            'description': Textarea,
        }