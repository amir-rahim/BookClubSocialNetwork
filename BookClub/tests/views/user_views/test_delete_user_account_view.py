"""Test delete user account view."""
from django.contrib.messages import get_messages
from django.test import TestCase, tag
from django.urls import reverse

from BookClub.models import User
from BookClub.tests.helpers import LogInTester


@tag('user', 'delete_user_account')
class DeleteUserAccountView(TestCase, LogInTester):
    """Test the Delete User Account view."""

    fixtures = [
        "BookClub/tests/fixtures/default_users.json"
    ]

    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.user_count = User.objects.all().count()
        self.url = reverse('delete_user_account')

    def test_delete_user_account_url(self):
        self.assertEqual(self.url, f'/user/delete/')

    def test_get_delete_user_account_redirects_to_home(self):
        """Test for redirecting user to logged out home page when account deleted."""
        self.client.login(username=self.user.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url)
        redirect_url = reverse('home')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_delete_user_account_not_logged_in_redirect(self):
        """Test guest cannot delete account"""
        self.assertFalse(self._is_logged_in())
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        self.client.post(self.url)
        user_count_after = User.objects.all().count()
        self.assertEqual(self.user_count, user_count_after)

    def test_successful_account_delete(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        user_count_after = User.objects.all().count()
        self.assertEqual(self.user_count, user_count_after + 1)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'You have successfully deleted your account.')

