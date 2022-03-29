"""Tests of the profile view."""
from django.test import TestCase, tag
from django.urls import reverse

from BookClub.models import User, Club


@tag('user', 'user_memberships')
class UserProfileMembershipsViewTest(TestCase):
    """Unit tests of the profile view."""

    fixtures = [
        'BookClub/tests/fixtures/default_users.json',
        'BookClub/tests/fixtures/default_clubs.json',
        'BookClub/tests/fixtures/default_memberships.json',
    ]

    def setUp(self):
        self.login_user = User.objects.get(username='johndoe')
        self.view_user = User.objects.get(username='amirdoe')
        self.view_user_2 = User.objects.get(pk=2)
        self.url = reverse('user_memberships', kwargs={"username": self.view_user.username})
        self.url_2 = reverse('user_memberships', kwargs={"username": self.view_user_2.username})

    def test_page_url(self):
        self.assertEqual(self.url, '/profile/amirdoe/memberships/')

    def test_template_used(self):
        self.client.login(username=self.login_user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'user/user_profile_memberships.html')

    def test_no_club(self):
        self.client.login(username=self.login_user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        clubs = list(response.context['clubs'])
        self.assertEqual(len(clubs), 0)

    def test_club(self):
        self.client.login(username=self.login_user.username, password='Password123')
        response = self.client.get(self.url_2)
        self.assertEqual(response.status_code, 200)
        clubs = list(response.context['clubs'])
        self.assertEqual(len(clubs), 2)

    def test_not_contains_club_not_member_of(self):
        self.client.login(username=self.login_user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        clubs = list(response.context['clubs'])
        self.assertNotIn(Club.objects.get(name="Jeannette Club"), clubs)
        self.assertNotContains(response, "<td>Jeannettes Club</td>")
