from django.contrib.messages import get_messages
from django.test import TestCase, tag
from django.urls import reverse

from BookClub.models import Book, User
from BookClub.tests.helpers import reverse_with_next


@tag("views", "bookshelf", "update_bookshelf")
class UpdateBookShelfViewTestCase(TestCase):
    """Test update book from bookshelf"""
    fixtures = [
        'BookClub/tests/fixtures/default_books.json',
        'BookClub/tests/fixtures/default_users.json',
        'BookClub/tests/fixtures/default_bookshelves.json'
    ]

    def setUp(self):
        self.user_none = User.objects.get(pk=2)
        self.user = User.objects.get(pk=1)
        self.book = Book.objects.get(pk=1)
        self.url = reverse('update_from_bookshelf', kwargs={"book_id": self.book.id})
        self.data = {'status': 1}

    def test_url(self):
        self.assertEquals(self.url, "/bookshelf/1/update/")

    def test_redirect_when_not_logged_in(self):
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.post(self.url, follow=True)
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200, fetch_redirect_response=True
                             )

    def test_get_url(self):
        self.client.login(username=self.user_none.username, password="Password123")
        redirect_url = reverse('bookshelf')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200, fetch_redirect_response=True
                             )

    """Updating books from each status"""

    def test_update_book_to_read(self):
        self.client.login(username=self.user.username, password="Password123")
        # Change status to Reading (status 0)
        url = reverse('update_from_bookshelf', kwargs={"book_id": 3})
        self.data['status'] = 0
        response = self.client.post(url, self.data, follow=True)
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'You have moved this book.')

    def test_update_book_to_reading(self):
        self.client.login(username=self.user.username, password="Password123")
        # Change status to Reading (status 1)
        response = self.client.post(self.url, self.data, follow=True)
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'You have moved this book.')

    def test_update_book_to_on_hold(self):
        self.client.login(username=self.user.username, password="Password123")
        # Change status to On Hold (status 2)
        self.data['status'] = 2
        response = self.client.post(self.url, self.data, follow=True)
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'You have moved this book.')

    def test_update_book_to_completed(self):
        self.client.login(username=self.user.username, password="Password123")
        # Change status to Completed (status 3)
        self.data['status'] = 3
        response = self.client.post(self.url, self.data, follow=True)
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'You have moved this book.')

    """Error handling"""

    def test_update_book_input_not_found(self):
        """Non-existent book"""
        self.client.login(username=self.user.username, password="Password123")
        url = reverse('update_from_bookshelf', kwargs={"book_id": 10000})
        response = self.client.post(url, self.data, follow=True)
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Error, book or bookshelf not found.')

    def test_update_status_input_not_found(self):
        """Non-existent status"""
        self.client.login(username=self.user.username, password="Password123")
        self.data['status'] = 6
        response = self.client.post(self.url, self.data, follow=True)
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'You cannot move that book!')

    def test_update_book_not_in_bookshelf(self):
        self.client.login(username=self.user_none.username, password="Password123")
        response = self.client.post(self.url, self.data, follow=True)
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'You cannot move that book!')


