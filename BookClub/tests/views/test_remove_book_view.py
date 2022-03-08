from django.test import TestCase, tag
from django.urls import reverse
from django.contrib.messages import get_messages
from BookClub.tests.helpers import LogInTester
from BookClub.models import User, BookList, Book

@tag("removebook")
class RemoveBookViewTestCase(TestCase, LogInTester):
    """Tests of the Join Meeting view."""

    fixtures = [
        'BookClub/tests/fixtures/default_users.json',
        'BookClub/tests/fixtures/default_books.json',
        'BookClub/tests/fixtures/booklists.json'
    ]

    def setUp(self):
        self.books = Book.objects.get(pk=1)
        self.id = BookList.objects.get(pk=1)
        self.user = User.objects.get(pk=1)

        self.url = reverse('remove_book', kwargs={'username' : self.user.username, 'booklist_id': self.id.id, 'book_id' : self.books.id})

    def test_url(self):
        self.assertEqual(self.url,f'/user/{self.user.username}/lists/{self.id.id}/{self.books.id}/delete')

    def test_redirect_when_not_logged_in(self):
        self.assertFalse(self._is_logged_in())
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_get_remove_book_redirects_to_user_booklist(self):
        """Test for redirecting user to user booklist when used get method."""

        self.client.login(username=self.user.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        response = self.client.get(reverse('remove_book', kwargs={'username' : self.user.username, 'booklist_id': self.id.id, 'book_id' : self.books.id}))
        redirect_url = reverse('user_booklist', kwargs={'username' : self.user.username,'booklist_id' : self.id.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_successful_remove_book(self):
        self.client.login(username=self.user.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        before_count = len(self.id.get_books())
        response = self.client.post(reverse('remove_book', kwargs={
                                                                'username' : self.user.username,
                                                                'booklist_id' : self.id.id,
                                                                'book_id' : self.books.id
                                                            }))     
        after_count = self.id.get_books().count()
        self.assertEqual(before_count, after_count + 1)                                                     
        self.assertFalse(self.id.get_books().filter(pk=self.books.id).exists())
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'You have removed the book.')

    def test_cannot_remove_book_if_not_creator(self):
        other_user = User.objects.get(pk=2)
        self.client.login(username=other_user.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        before_count = len(self.id.get_books())
        response = self.client.post(reverse('remove_book', kwargs={
                                                                'username' : self.user.username,
                                                                'booklist_id' : self.id.id,
                                                                'book_id' :  self.books.id
                                                            }))     
        after_count = self.id.get_books().count()
        self.assertEqual(before_count, after_count)                                                     
        self.assertTrue(self.id.get_books().filter(pk = self.books.id).exists())
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'You cannot remove that book!')

    def test_cannot_remove_invalid_book(self):
        self.client.login(username=self.user.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        before_count = len(self.id.get_books())
        response = self.client.post(reverse('remove_book', kwargs={
                                                                'username' : self.user.username,
                                                                'booklist_id' : self.id.id,
                                                                'book_id' : 100
                                                            }))     
        after_count = self.id.get_books().count()
        self.assertEqual(before_count, after_count)                                                     
        self.assertFalse(self.id.get_books().filter(pk=100).exists())
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Error, book or booklist not found.')

    def test_cannot_remove_from_invalid_booklist(self):
        self.client.login(username=self.user.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        before_count = len(self.id.get_books())
        response = self.client.post(reverse('remove_book', kwargs={
                                                                'username' : self.user.username,
                                                                'booklist_id' : 10000,
                                                                'book_id' : self.books.id
                                                            }))     
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Error, book or booklist not found.')