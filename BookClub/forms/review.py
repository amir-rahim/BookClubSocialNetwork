from django.forms import ModelForm, Textarea, ValidationError
from django.core.validators import RegexValidator
from django.test import tag
from BookClub.models import User, Book, BookReview
from BookClub.models.review import BookReviewComment


class ReviewForm(ModelForm):
    class Meta:
        model = BookReview

        fields = ['rating', 'content','title']

        widgets = {
            'content': Textarea,
        }

        labels = {
            'rating': 'Rating'
        }

class BookReviewCommentForm(ModelForm):
    class Meta:
        model = BookReviewComment

        fields = ['content']
        
        widgets = {
            'content': Textarea,
        }
        