import unittest
from django import forms
from django.test import TestCase, tag
from BookClub.models.review import *
from BookClub.forms.review import BookReviewCommentForm, ReviewForm
from django.db import IntegrityError

from datetime import date
@tag('reviewform','review','reviewformtest')
class ReviewFormTestCase(TestCase):
    """Unit tests for Review Form"""
    def setUp(self):
        self.form_input = {
            'bookrating': 7,
            'title': 'Review Title',
            'content': 'This book is definitely above the average, however, I disagree with the overall conclusion the author draws'
            # field created_on is omitted because the model automatically adds the date on save
        }

    def test_valid_review_form(self):
        form = ReviewForm(data = self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_has_strictly_necessary_fields(self):
        form = ReviewForm()
        self.assertIn('bookrating', form.fields)
        self.assertIn('content', form.fields)
        self.assertIn('title',form.fields)
        self.assertNotIn('book', form.fields)
        self.assertNotIn('creator', form.fields)
        self.assertNotIn('created_on', form.fields)

    def test_form_uses_model_validation(self):
        self.form_input['content'] = 'x' * 1025
        form = ReviewForm(data = self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_cannot_save_by_itself(self):
        form = ReviewForm(data = self.form_input)
        before_count = BookReview.objects.count()
        with self.assertRaises(IntegrityError):
            form.save()

@tag('review','form','reviewform','reviewcommentform','comment')
class BookReviewCommentFormTestCase(TestCase):
    def setUp(self):
        self.form_input = {
            'content': "New comment"
        }

    def test_valid_book_review_comment_form(self):
        form = BookReviewCommentForm(data = self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_has_necessary_field(self):
        form = BookReviewCommentForm()
        self.assertIn("content",form.fields)

    def test_form_uses_model_validation_illegal(self):
        self.form_input['content'] = 'x' * 241
        form = BookReviewCommentForm(data = self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_uses_model_validation_legal(self):
        self.form_input['content'] = 'x' * 240
        form = BookReviewCommentForm(data = self.form_input)
        self.assertTrue(form.is_valid())

    @unittest.expectedFailure
    def test_form_cannot_save_by_itself(self):
        form = BookReviewCommentForm(data = self.form_input)
        form.save()
        with self.assertRaises(IntegrityError):
            form.save()
        