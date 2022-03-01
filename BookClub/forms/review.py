from django.forms import ModelForm, Textarea, ValidationError
from django.core.validators import RegexValidator
from django.test import tag
from BookClub.models import User, Book, BookReview


class ReviewForm(ModelForm):
    class Meta:
        model = BookReview

        fields = ['rating', 'review']

        widgets = {
            'review': Textarea,
        }

        labels = {
            'rating': 'Rating'
        }
