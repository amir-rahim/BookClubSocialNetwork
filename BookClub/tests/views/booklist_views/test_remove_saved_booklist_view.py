from django.test import TestCase, tag
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.messages import get_messages

from BookClub.models import User, BookList
from BookClub.tests.helpers import reverse_with_next


@tag("booklist", "save_list")
class RemoveSavedBookListViewTestcase(TestCase):
    fixtures = [
        "BookClub/tests/fixtures/default_users.json",
        "BookClub/tests/fixtures/booklists.json",
        "BookClub/tests/fixtures/default_books.json"
    ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.creator = User.objects.get(pk=1)
        self.booklist_to_save = BookList.objects.get(pk=1)
        self.user = User.objects.get(pk=2)
        self.url = reverse('remove_saved_booklist', kwargs={'booklist_id': self.booklist_to_save.id})

    def test_save_booklist_url(self):
        self.assertEqual(self.url, f'/library/lists/{self.booklist_to_save.id}/remove_saved_booklist/')

    def test_remove_booklist_redirects_when_not_logged_in(self):
        before_count = BookList.objects.count()
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.post(self.url, follow=True)
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200, fetch_redirect_response=True
                             )
        self.assertTemplateUsed(response, 'authentication/login.html')
        after_count = BookList.objects.count()
        self.assertEqual(before_count, after_count)

    def test_get_remove_booklist_redirects_to_user_booklist(self):
        """Test for redirecting user to user booklist when used get method."""

        self.client.login(username=self.user.username, password='Password123')

        response = self.client.get(self.url)
        redirect_url = reverse('user_booklist', kwargs={'booklist_id': self.booklist_to_save.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_remove_invalid_booklist(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.post(reverse('remove_saved_booklist', kwargs={
            'booklist_id': 10
        }))
        with self.assertRaises(ObjectDoesNotExist):
            BookList.objects.get(id=10).exists()
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Error, invalid booklist.")

    def test_successful_remove_booklist(self):
        self.client.login(username=self.user.username, password='Password123')
        self.user.save_booklist(self.booklist_to_save)
        before_count = self.user.get_saved_booklists().count()
        response = self.client.post(self.url)
        after_count = self.user.get_saved_booklists().count()
        self.assertEqual(before_count - 1, after_count)
        self.assertFalse(self.user.get_saved_booklists().filter(id=1).exists())
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "You have removed the book list from saved.")

    def test_cannot_remove_booklist_not_in_saved(self):
        self.client.login(username=self.user.username, password='Password123')
        before_count = self.user.get_saved_booklists().count()
        response = self.client.post(self.url)
        after_count = self.user.get_saved_booklists().count()
        self.assertEqual(before_count, after_count)
        self.assertFalse(self.user.get_saved_booklists().filter(id=1).exists())
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "You cannot remove this book list from saved.")

    def test_cannot_remove_from_others_saved_booklists(self):
        own_booklist = BookList.objects.get(id=2)
        self.creator.save_booklist(own_booklist)
        url = reverse('remove_saved_booklist', kwargs={'booklist_id': own_booklist.id})
        self.client.login(username=self.user.username, password='Password123')
        before_count = self.creator.get_saved_booklists().count()
        response = self.client.post(url)
        after_count = self.creator.get_saved_booklists().count()
        self.assertEqual(before_count, after_count)
        self.assertTrue(self.creator.get_saved_booklists().filter(id=2).exists())
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "You cannot remove this book list from saved.")
