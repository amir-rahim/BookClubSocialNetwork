"""Unit tests for Feature Book Form"""
from django.test import TestCase, tag

from BookClub.forms import FeatureBookForm
from BookClub.models import Club, Book, FeaturedBooks


@tag('forms', 'feature_book')
class FeatureBookFormTestCase(TestCase):
    """Feature Book Form Tests"""

    fixtures = [
        'BookClub/tests/fixtures/default_books.json',
        'BookClub/tests/fixtures/default_clubs.json',
    ]

    def setUp(self):
        self.club = Club.objects.get(pk=1)
        self.form_input = {
            'club_id': self.club.id,
            'book': 1,
            'reason': 'This is a good book'
        }

    def test_valid_feature_book_form(self):
        form = FeatureBookForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_feature_book_form_must_save_correctly(self):
        form = FeatureBookForm(data = self.form_input)
        form.instance.club = self.club
        book = Book.objects.get(id=self.form_input['book'])
        before_count = FeaturedBooks.objects.count()
        featured_book = form.save()
        after_count = FeaturedBooks.objects.count()
        self.assertEqual(after_count, before_count + 1)
        self.assertEqual(featured_book.book, book)
        self.assertEqual(featured_book.reason, self.form_input['reason'])

    def test_feature_book_form_has_necessary_fields(self):
        form = FeatureBookForm()
        self.assertIn('book', form.fields)
        self.assertIn('reason', form.fields)

    def test_feature_book_form_uses_model_validation(self):
        self.form_input['reason'] = 'x' * 51
        form = FeatureBookForm(data=self.form_input)
        self.assertFalse(form.is_valid())

