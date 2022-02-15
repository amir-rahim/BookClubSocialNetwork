"""Tests of the Join Club view."""
from django.test import TestCase
from django.urls import reverse
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from BookClub.models import User, Club, ClubMembership

class MemberListTestCase(TestCase):
    """Tests of the Member List view."""

    fixtures = [
        'BookClub/tests/fixtures/default_users.json',
        'BookClub/tests/fixtures/default_clubs.json',
        'BookClub/tests/fixtures/default_memberships.json',
    ]
    
    def setUp(self):
        self.club = Club.objects.get(pk=1)
        self.url = reverse('member_list', kwargs={'url_name': self.club.url_name})
        self.user = User.objects.get(username="johndoe")
        self.jack = User.objects.get(username="jackdoe")
        self.jane = User.objects.get(username="janedoe")
        self.owner = Club.objects.get(pk=1).get_owner()
        self.moderators = Club.objects.get(pk=1).get_moderators()
        self.members = Club.objects.get(pk=1).get_members()
        
    def test_url(self):
        self.assertEqual(self.url, '/club/'+self.club.url_name+'/member_list/')
        
    def test_get_template_logged_in(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_members.html')
        
    def test_redirect_when_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
    
    def test_owner_has_admin_options(self):
        self.client.login(username=self.jane.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Club Administration")
        self.assertContains(response, "Manage Club")
        self.assertContains(response, "Club Settings")

    def test_mod_has_no_admin_options(self):
        self.client.login(username=self.user.username, password="Password123")
        url = reverse("club_dashboard", kwargs={"club_url_name": self.club.url_name})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Club Administration")
        self.assertNotContains(response, "Manage Club")
        self.assertNotContains(response, "Club Settings")
    
    def test_member_has_no_admin_options(self):
        self.client.login(username=self.jack.username, password="Password123")
        url = reverse("club_dashboard", kwargs={"club_url_name": self.club.url_name})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Club Administration")
        self.assertNotContains(response, "Manage Club")
        self.assertNotContains(response, "Club Settings")
        
    
    