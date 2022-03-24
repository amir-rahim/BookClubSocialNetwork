from django.contrib.messages import get_messages
from django.test import TestCase, tag
from django.urls import reverse

from BookClub.models import Book, BookList, User


@tag("booklist", "add_book")
class AddBookViewTestCase(TestCase):
    fixtures = [
        'BookClub/tests/fixtures/default_books.json',
        'BookClub/tests/fixtures/default_users.json',
        'BookClub/tests/fixtures/booklists.json',
    ]

    def setUp(self):
        self.book = Book.objects.get(pk=2)
        self.booklist = BookList.objects.get(pk=1)
        self.user = User.objects.get(pk=1)
        self.url = reverse('library_books')

    def test_url(self):
        self.assertEquals(self.url, "/library/books/")

    def test_if_not_logged_in_show_link(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "library_books.html")

    def test_user_can_see_list_of_book_lists(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "library_books.html")
        self.assertContains(response, "Mythical List")
        self.assertContains(response, "Empty List")

        # Tests dropdown only contains default option

    def test_no_book_lists(self):
        user_with_no_lists = User.objects.get(pk=4)
        self.client.login(username=user_with_no_lists.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "library_books.html")
        html_code = '<select required id="booklist" name="booklist">\n <option value="" selected disabled hidden>Choose here</option>\n</select>'
        self.assertNotContains(response, html_code, html=True)

    def test_adds_book_to_book_list(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.post(reverse('add_to_book_list'), {'book': 2, 'booklist': 1})
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "library_books.html")
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'The book has been saved to ' + self.booklist.title)

    def test_cannot_add_same_book_twice(self):
        self.client.login(username=self.user.username, password="Password123")
        self.booklist.add_book(self.book)
        response = self.client.post(reverse('add_to_book_list'), {'book': 2, 'booklist': 1})
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "library_books.html")
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'This book is already in the list')

    def test_invalid_input(self):
        self.client.login(username=self.user.username, password="Password123")
        self.booklist.add_book(self.book)
        response = self.client.post(reverse('add_to_book_list'), {'book': 2, 'booklist': 1000})
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'There was an error finding the book or booklist')
