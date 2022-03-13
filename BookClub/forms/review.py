from django.forms import ModelForm, Textarea

from BookClub.models import BookReview


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
