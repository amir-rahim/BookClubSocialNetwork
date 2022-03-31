"""Tests of the booklists_list view."""
from django.test import TestCase, tag
from django.urls import reverse

from BookClub.models import User, BookList
from BookClub.tests.helpers import reverse_with_next


@tag("booklist", "list")
class UserBooklistsViewTestCase(TestCase):
    """Tests of the booklists_list view."""

    fixtures = [
        'BookClub/tests/fixtures/default_users.json',
        'BookClub/tests/fixtures/default_books.json',
        'BookClub/tests/fixtures/booklists.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username="johndoe")
        self.url = reverse('booklists_list')

    def _get_url_for_user(self, user):
        return reverse('booklists_list', kwargs={'username': user})

    def test_url(self):
        self.assertEqual(self.url, f"/library/lists/")

    def test_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.get(self.url, follow = True)
        self.assertRedirects(response, redirect_url,
            status_code=302, target_status_code=200, fetch_redirect_response=True
        )
        self.assertTemplateUsed(response, 'authentication/login.html')

    def test_get_template_logged_in(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'booklists/user_booklists.html')

    def test_get_user_template_logged_in(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self._get_url_for_user('johndoe'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['user'], self.user)
        self.assertTemplateUsed(response, 'booklists/user_booklists.html')

    def test_contains_lists_created_by_user(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'booklists/user_booklists.html')
        response_lists = list(response.context['booklists'])
        user_lists = list(BookList.objects.filter(creator=self.user))

        for userlist in user_lists:
            self.assertIn(userlist, response_lists)

    def test_does_not_contain_lists_created_by_other_users(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'booklists/user_booklists.html')
        response_lists = list(response.context['booklists'])
        lists_by_other_users = list(BookList.objects.exclude(creator=self.user))

        for userlist in lists_by_other_users:
            self.assertNotIn(lists_by_other_users, response_lists)

    def test_user_viewing_own_lists_is_recognized(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'booklists/user_booklists.html')
        self.assertEqual(response.context['own'], True)
        self.assertContains(response, '<span>Edit</span>')

    def test_user_viewing_not_own_lists_is_recognized(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self._get_url_for_user('janedoe'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'booklists/user_booklists.html')
        self.assertEqual(response.context['own'], False)

    def test_view_lists_of_another_user_without_lists(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self._get_url_for_user('sebdoe'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'booklists/user_booklists.html')
        response_lists = list(response.context['booklists'])
        self.assertEqual(len(response_lists), 0)
        self.assertContains(response, 'No lists.')

    def test_user_without_lists_viewing_own_lists(self):
        self.client.login(username=self.user.username, password='Password123')
        BookList.objects.all().delete()
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'booklists/user_booklists.html')
        response_lists = list(response.context['booklists'])
        self.assertEqual(len(response_lists), 0)
        self.assertContains(response, "No lists.")
        self.assertContains(response, "Create one?")
