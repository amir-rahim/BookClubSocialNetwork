"""Unit testing for Saved Booklist List view"""
from django.test import TestCase, tag
from django.urls import reverse

from BookClub.models import User, BookList
from BookClub.tests.helpers import LogInTester, reverse_with_next


@tag("booklist", "save_list")
class SavedBookListsViewTestCase(TestCase, LogInTester):
    """Saved Booklist lists view testing"""
    fixtures = [
        'BookClub/tests/fixtures/default_users.json',
        'BookClub/tests/fixtures/default_books.json',
        'BookClub/tests/fixtures/booklists.json'
    ]

    def setUp(self):
        self.creator = User.objects.get(pk=1)
        self.user = User.objects.get(pk=2)
        self.booklist_to_save = BookList.objects.get(pk = 1)
        self.own_booklist = BookList.objects.get(pk = 2)

        self.url = reverse('saved_booklists')

    def test_url(self):
        self.assertEqual(self.url, f'/library/lists/saved/')

    def test_get_template(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'booklists/saved_booklists.html')

    def _get_url_for_user(self, username):
        return reverse('saved_booklists', kwargs={'username': username})

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
        self.assertTemplateUsed(response, 'booklists/saved_booklists.html')
       

    def test_not_contains_booklists_created_by_user(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.user.save_booklist(self.own_booklist)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'booklists/saved_booklists.html')
        
        response_lists = list(response.context['booklists'])
        user_lists = list(BookList.objects.filter(creator=self.user))

        for userlist in user_lists:
            self.assertNotIn(userlist, response_lists)
        
    def test_does_contain_lists_created_by_other_users(self):
        self.client.login(username=self.user.username, password='Password123')
        self.user.save_booklist(self.booklist_to_save)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'booklists/saved_booklists.html')
        response_lists = list(response.context['booklists'])
        lists_by_other_users = self.user.get_saved_booklists()

        for userlist in lists_by_other_users:
            self.assertIn(userlist, response_lists)

    def test_user_viewing_own_saved_booklists_is_recognized(self):
        self.client.login(username=self.user.username, password='Password123')
        self.user.save_booklist(self.booklist_to_save)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'booklists/saved_booklists.html')
        self.assertEqual(response.context['own'], True)
        self.assertContains(response, 'Remove from saved')

    def test_user_can_view_other_users_saved_booklists_list(self):
        self.client.login(username=self.user.username, password='Password123')
        self.creator.save_booklist(self.own_booklist)
        url = reverse('saved_booklists', kwargs={'username': self.creator.username})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'booklists/saved_booklists.html')
        response_lists = list(response.context['booklists'])
        lists_by_other_users = self.creator.get_saved_booklists()

        for userlist in lists_by_other_users:
            self.assertIn(userlist, response_lists)

    def test_user_without_saved_booklists_viewing_own_saved_booklists(self):
        self.client.login(username=self.user.username, password='Password123')
        url = reverse('saved_booklists', kwargs={'username': self.user.username})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'booklists/saved_booklists.html')
        response_lists = list(response.context['booklists'])
        self.assertEqual(len(response_lists), 0)
        self.assertContains(response, "No saved lists.")

