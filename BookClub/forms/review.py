from django.forms import ModelForm, Textarea, ValidationError
from django.core.validators import RegexValidator
from django.test import tag
from BookClub.models import User, Book
from BookClub.models.review import *


class ReviewForm(ModelForm):
    class Meta:
        model = BookReview

        fields = ['bookrating', 'content','title']

        widgets = {
            'content': Textarea,
        }

        labels = {
            'bookrating': 'Rating'
        }

class BookReviewCommentForm(ModelForm):
    class Meta:
        model = BookReviewComment

        fields = ['content']
        
        widgets = {
            'content': Textarea,
        }
