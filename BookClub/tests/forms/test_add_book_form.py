from django.test import TestCase, tag

from BookClub.forms import AddBookForm
from BookClub.models import Book, BookList


@tag('forms', 'book', 'add_book')
class AddBookFormTestCase(TestCase):
    fixtures = [
        "BookClub/tests/fixtures/default_users.json",
        "BookClub/tests/fixtures/default_books.json",
        "BookClub/tests/fixtures/booklists.json",
    ]
    """Unit tests for Add Book Form"""

    def setUp(self):
        self.book = Book.objects.get(pk=2)
        self.booklist = BookList.objects.get(pk=1)
        self.form_input = {
            'book': 2,
            'booklist': 1
        }

    def test_valid_add_book_form(self):
        form = AddBookForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_has_necessary_fields(self):
        form = AddBookForm(data=self.form_input)
        self.assertIn('book', form.fields)
        self.assertIn('booklist', form.fields)

    def test_form_must_save_correctly(self):
        form = AddBookForm(data=self.form_input)
        self.assertTrue(form.is_valid())
        self.assertEqual(form['book'].value(), self.book.id)
        self.assertEqual(form['booklist'].value(), self.booklist.id)
