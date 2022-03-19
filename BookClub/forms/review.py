from django.forms import ModelForm, Textarea

from BookClub.models import BookReview, BookReviewComment


class ReviewForm(ModelForm):
    class Meta:
        model = BookReview

        fields = ['book_rating', 'title', 'content']

        widgets = {
            'content': Textarea,
        }

        labels = {
            'book_rating': 'Rating'
        }


class BookReviewCommentForm(ModelForm):
    class Meta:
        model = BookReviewComment

        fields = ['content']

        widgets = {
            'content': Textarea,
        }
