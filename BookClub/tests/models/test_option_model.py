"""Test case for Option model"""
from django.core.exceptions import ValidationError
from django.test import TestCase, tag

from BookClub.models import Option, Poll, Book


@tag('models', 'options')
class OptionModelTestCase(TestCase):
    fixtures = [
        'BookClub/tests/fixtures/default_books.json',
        'BookClub/tests/fixtures/default_users.json',
        'BookClub/tests/fixtures/default_clubs.json',
        'BookClub/tests/fixtures/default_polls.json',
        'BookClub/tests/fixtures/default_options.json'
    ]

    def setUp(self):
        self.option = Option.objects.get(pk=1)
        self.poll = Poll.objects.get(pk=1)
        self.book = Book.objects.get(pk=1)

    def _assert_option_is_valid(self):
        try:
            self.option.full_clean()
        except ValidationError:
            self.fail('Test option should be valid')

    def _assert_option_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.option.full_clean()

    # Fields testing

    # Tests of text attribute

    def test_text_cannot_be_blank(self):
        self.option.text = None
        self._assert_option_is_invalid()
        self.option.text = ""
        self._assert_option_is_invalid()

    def test_text_can_be_between_1_and_120_characters_long(self):
        self.option.text = 'x' * 1
        self._assert_option_is_valid()
        self.option.text = 'x' * 120
        self._assert_option_is_valid()

    def test_text_cannot_be_more_than_120_characters_long(self):
        self.option.text = 'x' * 121
        self._assert_option_is_invalid()

    # Tests of poll attribute

    def test_poll_cannot_be_null(self):
        self.option.poll = None
        self._assert_option_is_invalid()

    def test_poll_is_poll_object(self):
        self.option.poll = self.poll
        self._assert_option_is_valid()

    def test_poll_deleted_cascade(self):
        self.option.poll = self.poll
        self._assert_option_is_valid
        self.poll.delete()
        with self.assertRaises(Option.DoesNotExist):
            Option.objects.get(pk=1)

    # Tests of book attribute

    def test_book_can_be_null(self):
        self.option.book = None
        self._assert_option_is_valid()

    def test_book_is_book_object(self):
        self.option.book = self.book
        self._assert_option_is_valid()

    def test_book_deleted_set_null(self):
        self.option.book = self.book
        self._assert_option_is_valid()
        self.book.delete()
        option = Option.objects.get(pk=1)
        self.assertEqual(option.book, None)
