"""Unit testing of the add book to bookshelf view"""
from django.contrib.messages import get_messages
from django.test import TestCase, tag
from django.urls import reverse

from BookClub.models import Book, User
from BookClub.tests.helpers import reverse_with_next


@tag("views", "bookshelf", "add_bookshelf")
class AddBookShelfViewTestCase(TestCase):
    """Test add book to bookshelf view"""
    fixtures = [
        'BookClub/tests/fixtures/default_books.json',
        'BookClub/tests/fixtures/default_users.json',
        'BookClub/tests/fixtures/default_bookshelves.json'
    ]

    def setUp(self):
        self.user_none = User.objects.get(pk=2)
        self.user = User.objects.get(pk=1)
        self.book = Book.objects.get(pk=1)
        self.url = reverse('add_to_bookshelf', kwargs={"book_id": self.book.id})
        self.data = {'status': 1}

    def test_url(self):
        self.assertEquals(self.url, "/bookshelf/1/add/")

    def test_redirect_when_not_logged_in(self):
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.post(self.url, self.data, follow=True)
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200, fetch_redirect_response=True
                             )

    def test_get_url(self):
        self.client.login(username=self.user_none.username, password="Password123")
        redirect_url = reverse('library_books')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200, fetch_redirect_response=True
                             )

    def test_adds_book_to_bookshelf(self):
        self.client.login(username=self.user_none.username, password="Password123")
        response = self.client.post(self.url, self.data, follow=True)
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'You have added the book to your bookshelf.')

    def test_invalid_input(self):
        self.client.login(username=self.user_none.username, password="Password123")
        # create invalid input
        self.data['status'] = 5
        response = self.client.post(self.url, self.data, follow=True)
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'You cannot add that book!')

    def test_does_not_add_same_book_same_status(self):
        self.client.login(username=self.user.username, password="Password123")
        # add book 1 to same to_read bookshelf
        self.data['status'] = 0
        response = self.client.post(self.url, self.data, follow=True)
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'You cannot add that book!')

    def test_does_not_add_same_book_other_status(self):
        self.client.login(username=self.user.username, password="Password123")
        # add book 1 to another shelf
        self.data['status'] = 3
        response = self.client.post(self.url, self.data, follow=True)
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'You cannot add that book!')

    def test_book_not_found(self):
        self.client.login(username=self.user.username, password="Password123")
        # Add non-existent status
        url = reverse('add_to_bookshelf', kwargs={"book_id": 555555})
        response = self.client.post(url, self.data, follow=True)
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Error, book or bookshelf not found.')


