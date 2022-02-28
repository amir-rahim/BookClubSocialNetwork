"""Tests of the profile view."""

from django.test import TestCase, tag
from django.urls import reverse
from BookClub.models import User, ClubMembership, Club
from BookClub.tests.helpers import reverse_with_query

@tag('profile','user','following')

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
        self.url = reverse('user_following', kwargs={"username": self.view_user.username})
        self.url_2 = reverse('user_following', kwargs={"username": self.view_user_2.username})
        
    def test_page_url(self):
        self.assertEqual(self.url, '/profile/amirdoe/following/')
        
    def test_template_used(self):
        self.client.login(username=self.login_user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'user_profile_following.html')
        
    def test_no_following(self):
        self.client.login(username=self.login_user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        following = list(response.context['following'])
        self.assertEqual(len(following), 0)
        
    def test_not_contains_club_not_member_of(self):
        self.client.login(username=self.login_user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        following = list(response.context['following'])
        self.assertNotIn(User.objects.get(username="jackdoe"), following)
        self.assertNotContains(response, "<td>jackdoe</td>")