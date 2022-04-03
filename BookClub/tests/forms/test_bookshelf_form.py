"""Unit tests for bookshelf form"""
from django.test import TestCase, tag

from BookClub.forms import AddBookShelfForm
from BookClub.models import Book, User


@tag('forms', 'bookshelf')
class AddBookShelfFormTestCase(TestCase):
    """Adding a Book to a Bookshelf Form Test"""
    fixtures = [
        "BookClub/tests/fixtures/default_users.json",
        "BookClub/tests/fixtures/default_books.json",
    ]

    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.book = Book.objects.get(pk=1)
        self.form_input = {
            'user': 1,
            'book': 1,
            'status': 0
        }

    def test_valid_add_bookshelf_form(self):
        form = AddBookShelfForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_has_necessary_fields(self):
        form = AddBookShelfForm(data=self.form_input)
        self.assertIn('user', form.fields)
        self.assertIn('book', form.fields)
        self.assertIn('status', form.fields)

    def test_form_must_save_correctly(self):
        form = AddBookShelfForm(data=self.form_input)
        self.assertTrue(form.is_valid())
        self.assertEqual(form['user'].value(), self.user.id)
        self.assertEqual(form['book'].value(), self.book.id)
        self.assertEqual(form['status'].value(), 0)
