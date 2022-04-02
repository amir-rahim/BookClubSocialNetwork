"""Unit testing of the Bookshelf Model"""
from django.forms import ValidationError
from django.test import TestCase, tag

from BookClub.models import Book, User, BookShelf


@tag('models', 'bookshelf')
class BookShelfTestCase(TestCase):
    """Bookshelf Model, Fields, Validation and Methods Testing"""
    fixtures = [
        'BookClub/tests/fixtures/default_books.json',
        'BookClub/tests/fixtures/default_users.json',
        'BookClub/tests/fixtures/default_bookshelves.json'
    ]

    def setUp(self):
        self.book_one = Book.objects.get(pk=1)
        self.book_two = Book.objects.get(pk=2)
        self.book_three = Book.objects.get(pk=3)
        self.book_four = Book.objects.get(pk=4)
        self.user = User.objects.get(pk=1)
        self.bookshelf = BookShelf.objects.get(pk=1)

    def _assert_bookshelf_is_valid(self):
        try:
            self.bookshelf.full_clean()
        except(ValidationError):
            self.fail('Book shelf should be valid')

    def _assert_bookshelf_is_invalid(self):
        with self.assertRaises(Exception):
            self.bookshelf.full_clean()

    """Test null fields"""

    def test_user_cannot_be_null(self):
        self.bookshelf.user = None
        self._assert_bookshelf_is_invalid()

    def test_book_cannot_be_null(self):
        self.bookshelf.book = None
        self._assert_bookshelf_is_invalid()

    def test_status_cannot_be_null(self):
        self.bookshelf.status = None
        self._assert_bookshelf_is_invalid()

    """Test getting each list, and all combined lists"""

    def test_get_to_read(self):
        self.assertEqual(len(BookShelf.get_to_read(self.user)), 1)

    def test_get_reading(self):
        self.assertEqual(len(BookShelf.get_reading(self.user)), 1)
        
    def test_get_on_hold(self):
        self.assertEqual(len(BookShelf.get_on_hold(self.user)), 1)

    def test_get_completed(self):
        self.assertEqual(len(BookShelf.get_completed(self.user)), 1)

    def test_get_all_books(self):
        self.assertEqual(len(BookShelf.get_all_books(self.user)), 4)
        