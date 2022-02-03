"""Tests of the profile view."""

from django.test import TestCase
from django.urls import reverse
from BookClub.models import User
from BookClub.tests.helpers import reverse_with_query

class ProfileViewTest(TestCase):
    """Unit tests of the profile view."""

    fixtures = [
        'BookClub/tests/fixtures/default_users.json',
    ]

    def setUp(self):
        self.user = User.objects.get(username='johndoe')
        self.url = reverse('user_dashboard')

    def test_profile_url(self):
        self.assertEqual(self.url, '/user_dashboard/')

    def test_get_profile(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'templates/user_dashboard.html')


    def test_get_profile_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_query('login')
        response = self.client.get(self.url)
        self.assertRedirects(response,
                             redirect_url,
                             status_code=302,
                             target_status_code=200)

    
