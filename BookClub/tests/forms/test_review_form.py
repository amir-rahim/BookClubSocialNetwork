from django import forms
from django.test import TestCase, tag
from BookClub.models import BookReview
from BookClub.forms.review import ReviewForm
from django.db import IntegrityError

from datetime import date
@tag('reviewform','review')
class ReviewFormTestCase(TestCase):
    """Unit tests for Review Form"""
    def setUp(self):
        self.form_input = {
            'rating': 7,
            'review': 'This book is definitely above the average, however, I disagree with the overall conclusion the author draws'
            # field created_on is omitted because the model automatically adds the date on save
        }

    def test_valid_review_form(self):
        form = ReviewForm(data = self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_has_strictly_necessary_fields(self):
        form = ReviewForm()
        self.assertIn('rating', form.fields)
        self.assertIn('review', form.fields)
        self.assertNotIn('book', form.fields)
        self.assertNotIn('user', form.fields)
        self.assertNotIn('createdOn', form.fields)

    def test_form_uses_model_validation(self):
        self.form_input['review'] = 'x' * 1025
        form = ReviewForm(data = self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_cannot_save_by_itself(self):
        form = ReviewForm(data = self.form_input)
        before_count = BookReview.objects.count()
        with self.assertRaises(IntegrityError):
            form.save()
