"""Tests for editing book list details"""
from django.test import TestCase, tag
from django.urls import reverse
from BookClub.models import User, Book, BookList
from BookClub.tests.helpers import LogInTester, reverse_with_next
from django.contrib import messages
from django.contrib.messages import get_messages


@tag('booklist', 'editbooklist')
class EditBookListViewTestCase(TestCase, LogInTester):
    """Tests for editing book list details"""

    fixtures = [
        'BookClub/tests/fixtures/default_books.json',
        'BookClub/tests/fixtures/default_users.json',
        'BookClub/tests/fixtures/booklists.json',
    ]

    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.another_user = User.objects.get(pk=2)
        self.booklist = BookList.objects.get(pk=1)
        self.data = {
            'title': 'New title',
            'description': 'New description',
        }

        self.url = reverse('edit_booklist', kwargs={'username': self.user.username, 'booklist_id': self.booklist.id})

    def test_edit_booklist_url(self):
        self.assertEqual(self.url, f'/user/{self.user.username}/lists/{self.booklist.id}/edit/')

    def test_post_edit_booklist_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.post(self.url, self.data, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200, fetch_redirect_response=True)
        self.assertTemplateUsed(response, 'login.html')

    def test_edit_booklist_redirects_when_trying_to_edit_another_users_booklist(self):
        self.client.login(username=self.another_user.username, password="Password123")
        self.assertTrue(self._is_logged_in())
        redirect_url = reverse('booklists_list', kwargs={'username': self.user.username})
        response = self.client.post(self.url, self.data, follow=True)
        messages_list = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200, fetch_redirect_response=True)
        self.assertTemplateUsed(response, 'user_booklists.html')

    '''Tests for user successfully editing the book list details'''

    def test_successful_edit_booklist_details_when_logged_in_as_user(self):
        self.client.login(username=self.user.username, password="Password123")
        self.assertTrue(self._is_logged_in())
        response = self.client.post(self.url, self.data, follow=True)
        self.booklist.refresh_from_db()
        messages_list = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.SUCCESS)
        redirect_url = reverse('booklists_list', kwargs={'username': self.user.username})
        self.assertTemplateUsed(response, 'user_booklists.html')
        self.assertEqual(self.booklist.creator.id, self.user.id)
        self.assertEqual(self.booklist.title, self.data['title'])
        self.assertEqual(self.booklist.description, self.data['description'])
        self.assertRedirects(response, expected_url=redirect_url, status_code=302, target_status_code=200)

    def test_successful_edit_booklist_title_when_logged_in_as_user(self):
        self.client.login(username=self.user.username, password="Password123")
        self.assertTrue(self._is_logged_in())
        self.data['title'] = 'Lorem Ipsum'
        response = self.client.post(self.url, self.data, follow=True)
        self.booklist.refresh_from_db()
        messages_list = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.SUCCESS)
        redirect_url = reverse('booklists_list', kwargs={'username': self.user.username})
        self.assertTemplateUsed(response, 'user_booklists.html')
        self.assertEqual(self.booklist.creator.id, self.user.id)
        self.assertEqual(self.booklist.title, self.data['title'])
        self.assertEqual(self.booklist.description, self.data['description'])
        self.assertRedirects(response, expected_url=redirect_url, status_code=302, target_status_code=200)

    def test_successful_edit_booklist_description_when_logged_in_as_user(self):
        self.client.login(username=self.user.username, password="Password123")
        self.assertTrue(self._is_logged_in())
        self.data['description'] = 'Lorem Ipsum'
        response = self.client.post(self.url, self.data, follow=True)
        self.booklist.refresh_from_db()
        messages_list = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.SUCCESS)
        redirect_url = reverse('booklists_list', kwargs={'username': self.user.username})
        self.assertTemplateUsed(response, 'user_booklists.html')
        self.assertEqual(self.booklist.creator.id, self.user.id)
        self.assertEqual(self.booklist.title, self.data['title'])
        self.assertEqual(self.booklist.description, self.data['description'])
        self.assertRedirects(response, expected_url=redirect_url, status_code=302, target_status_code=200)

    '''Tests for user unsuccessfully editing the book list details'''

    def test_unsuccessful_edit_booklist_details_when_logged_in_as_user(self):
        self.client.login(username=self.user.username, password="Password123")
        self.assertTrue(self._is_logged_in())
        self.data['title'] = ''
        booklist_title_before = self.booklist.title
        booklist_description_before = self.booklist.description
        response = self.client.post(self.url, self.data, follow=True)
        self.booklist.refresh_from_db()
        self.assertTemplateUsed('edit_booklist.html')
        self.assertEqual(self.booklist.creator.id, self.user.id)
        self.assertEqual(self.booklist.title, booklist_title_before)
        self.assertEqual(self.booklist.description, booklist_description_before)

    def test_no_booklist_to_edit(self):
        self.client.login(username=self.user.username, password="Password123")
        self.assertTrue(self._is_logged_in())
        self.url = reverse('edit_booklist', kwargs={'username': self.user.username, 'booklist_id': self.booklist.id+9999})
        response = self.client.post(self.url, self.data, follow=True)
        redirect_url = reverse('booklists_list', kwargs={'username': self.user.username})
        messages_list = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200, fetch_redirect_response=True)
        self.assertTemplateUsed(response, 'user_booklists.html')
