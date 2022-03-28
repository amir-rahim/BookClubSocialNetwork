"""Tests of the profile view."""
from django.test import TestCase, tag
from django.urls import reverse

from BookClub.models import User


@tag('user', 'user_profile')
class UserProfileViewTest(TestCase):
    """Unit tests of the profile view."""

    fixtures = [
        'BookClub/tests/fixtures/default_users.json',
    ]

    def setUp(self):
        self.login_user = User.objects.get(username='johndoe')
        self.view_user = User.objects.get(username='jackdoe')
        self.url = reverse('user_profile', kwargs={"username": self.view_user.username})

    def test_profile_url(self):
        self.assertEqual(self.url, '/profile/jackdoe/')

    def test_get_profile(self):
        self.client.login(username=self.login_user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_dashboard.html')

    def test_get_info(self):
        self.client.login(username=self.login_user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertContains(response, "<h1 class=\"title\">jackdoe's Dashboard</h1>")
        self.assertContains(response, "<h2 class=\"subtitle\">Bookshelf</h2>")
        self.assertContains(response, "<b>Username: </b> jackdoe")
        self.assertContains(response, "<b>Public Bio: </b> " + self.view_user.public_bio)
