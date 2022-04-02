"""Unit testing of the Featured Books Model"""
from django.test import TestCase, tag
from django.core.exceptions import ValidationError

from BookClub.models import Club, Book, FeaturedBooks, featured_books


@tag('models', 'featured_books')
class FeaturedBooksModelTestCase(TestCase):
    """Featured Book Model, Fields, Validation and Methods Testing"""
    fixtures = [
        'BookClub/tests/fixtures/default_clubs.json',
        'BookClub/tests/fixtures/default_books.json',
    ]

    def setUp(self):
        self.club = Club.objects.get(pk=1)
        self.book = Book.objects.get(pk=1)
        self.club_featured_books = FeaturedBooks.objects.create(club=self.club, book=self.book, reason="A great read")

    def _assert_featured_books_is_valid(self):
        try:
            self.club_featured_books.full_clean()
        except ValidationError:
            self.fail('Test featured books should be valid')

    def _assert_featured_books_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.club_featured_books.full_clean()
    
    """Test model fields"""

    def test_club_cannot_be_null(self):
        self.club_featured_books.club = None
        self._assert_featured_books_is_invalid()

    def test_book_cannot_be_null(self):
        self.club_featured_books.book = None
        self._assert_featured_books_is_invalid()

    def test_reason_can_be_blank(self):
        self.club_featured_books.reason = ''
        self._assert_featured_books_is_valid()

    """Test methods"""

    def test_can_get_books(self):
        book_count = FeaturedBooks.get_books(self.club).count()
        self.assertEqual(1, book_count)
