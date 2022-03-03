import datetime
from django.forms import ValidationError
from BookClub.models import Book
from BookClub.models.booklist import BookList
from BookClub.models.user import User
from django.db import models
from django.test import TestCase, tag

@tag('booklist')
@tag('book')
class BookListTestCase(TestCase):

    fixtures=[
        'BookClub/tests/fixtures/default_books.json',
        'BookClub/tests/fixtures/default_users.json',
        'BookClub/tests/fixtures/booklists.json'
    ]

    def setUp(self):
        self.bookList = BookList.objects.get(pk=1)
        self.book_one = Book.objects.get(pk=1)
        self.book_two = Book.objects.get(pk=3)

    def _assert_booklist_is_valid(self):
        try:
            self.bookList.full_clean()
        except(ValidationError):
            self.fail('Book list should be valid')

    def _assert_booklist_is_invalid(self):
        with self.assertRaises(Exception):
            self.bookList.full_clean()


    # Title
    def test_title_cannot_be_blank(self):
        self.bookList.title = ''
        self._assert_booklist_is_invalid()

    def test_title_may_already_exist(self):
        second_list = BookList.objects.get(pk=2)
        self.bookList.title = second_list.title
        self._assert_booklist_is_valid()

    def test_title_can_be_120_characters_long(self):
        self.bookList.title = 'x' * 120
        self._assert_booklist_is_valid()

    def test_title_cannot_be_over_120_characters_long(self):
        self.bookList.title = 'x' * 121
        self._assert_booklist_is_invalid()


    # Description
    def test_description_can_be_blank(self):
        self.bookList.description = ''
        self._assert_booklist_is_valid()

    def test_description_may_already_exist(self):
        second_list = BookList.objects.get(pk=2)
        self.bookList.description = second_list.description
        self._assert_booklist_is_valid()

    def test_description_can_be_240_characters_long(self):
        self.bookList.description = 'x' * 240
        self._assert_booklist_is_valid()

    def test_description_cannot_be_over_240_characters_long(self):
        self.bookList.description = 'x' * 241
        self._assert_booklist_is_invalid()


    # Creator
    def test_creator_cannot_be_blank(self):
        self.bookList.creator = None
        self._assert_booklist_is_invalid()

    def test_creator_does_not_have_to_be_unique(self):
        second_list = BookList.objects.get(pk=2)
        self.bookList.creator = second_list.creator
        self._assert_booklist_is_valid()

    def test_booklist_is_deleted_when_creator_is_deleted(self):
        user = User.objects.get(pk = 1)
        user_booklist_count = BookList.objects.filter(creator = user).count()
        booklist_count_before = BookList.objects.count()
        user.delete()
        self.assertEqual(BookList.objects.count(), booklist_count_before - user_booklist_count)


    # Books
    def test_books_field_can_be_empty(self):
        self.bookList.books.set([])
        self._assert_booklist_is_valid()

    def test_books_set_does_not_have_to_be_unique(self):
        second_list = BookList.objects.get(pk=2)
        self.bookList.books.set(second_list.books.all())
        self._assert_booklist_is_valid()

    def test_add_book_to_list_works_correctly(self):
        books_in_the_list = []
        for book in self.bookList.books.all():
            books_in_the_list.append(book.pk)

        new_book_in_the_list = Book.objects.exclude(pk__in = books_in_the_list)[0]
        list_book_count_before = self.bookList.books.count()
        self.bookList.books.add(new_book_in_the_list)
        self.assertEqual(self.bookList.books.count(), list_book_count_before + 1)
        self.assertIn(new_book_in_the_list, self.bookList.books.all())
        self._assert_booklist_is_valid()

    def test_books_field_does_not_record_duplicates(self):
        books_in_the_list = []
        for book in self.bookList.books.all():
            books_in_the_list.append(book.pk)

        new_book_in_the_list = Book.objects.exclude(pk__in = books_in_the_list)[0]
        list_book_count_before = self.bookList.books.count()
        self.bookList.books.add(new_book_in_the_list)
        self.assertEqual(self.bookList.books.count(), list_book_count_before + 1)
        self.assertIn(new_book_in_the_list, self.bookList.books.all())

        # adding the same book again twice
        self.bookList.books.add(new_book_in_the_list)
        self.bookList.books.add(new_book_in_the_list)
        self.assertEqual(self.bookList.books.count(), list_book_count_before + 1)
        self.assertIn(new_book_in_the_list, self.bookList.books.all())

        self._assert_booklist_is_valid()

    def test_remove_from_list_works_correctly(self):
        first_book_in_the_list = self.bookList.books.all()[0]
        list_book_count_before = self.bookList.books.count()
        self.bookList.books.remove(first_book_in_the_list)
        self.assertEqual(self.bookList.books.count(), list_book_count_before - 1)
        self.assertNotIn(first_book_in_the_list, self.bookList.books.all())

    def test_deleted_book_is_removed_from_the_list_automatically(self):
        first_book_in_the_list = self.bookList.books.all()[0]
        list_book_count_before = self.bookList.books.count()
        first_book_in_the_list.delete()
        self.assertEqual(self.bookList.books.count(), list_book_count_before - 1)
        self.assertNotIn(first_book_in_the_list, self.bookList.books.all())

    # Check helper methods
    def test_get_delete_url(self):
        url_from_model = self.bookList.get_delete_url()
        correct_url = '/user/johndoe/list/1/delete/'
        self.assertEqual(url_from_model, correct_url)

    def test_string_function_returns_correct_value(self):
        strings_from_model = [self.bookList.__str__(), self.bookList.__str__(), self.bookList.__str__()]
        correct_string = f"Book List '{self.bookList.title}' with {self.bookList.books.count()} titles"
        for model_string in strings_from_model:
            self.assertEqual(model_string, correct_string)

    def test_get_books(self):
        self.assertQuerysetEqual(self.bookList.get_books(), [self.book_one, self.book_two], ordered = False)