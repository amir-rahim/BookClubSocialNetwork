"""Tests of the Join Club view."""
from ast import Pass
from email.mime import application
from django.test import TestCase, tag
from django.urls import reverse
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from BookClub.models import User, Club, ClubMembership
@tag('memberlist')
class MemberListTestCase(TestCase):
    """Tests of the Member List view."""

    fixtures = [
        'BookClub/tests/fixtures/default_users.json',
        'BookClub/tests/fixtures/default_clubs.json',
        'BookClub/tests/fixtures/default_memberships.json',
    ]
    
    def setUp(self):
        self.club = Club.objects.get(pk=1)
        self.url = reverse('member_list', kwargs={'club_url_name': self.club.club_url_name})
        self.user = User.objects.get(username="johndoe")
        self.jack = User.objects.get(username="jackdoe")
        self.jane = User.objects.get(username="janedoe")
        self.owner = Club.objects.get(pk=1).get_owner()[0]
        self.moderators = Club.objects.get(pk=1).get_moderators()
        self.members = Club.objects.get(pk=1).get_members()
        self.applicants = Club.objects.get(pk=1).get_applicants()
        
    def test_url(self):
        self.assertEqual(self.url, '/club/'+self.club.club_url_name+'/member_list/')
        
    def test_get_template_logged_in(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_members.html')
        
    def test_redirect_when_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
    
    def test_can_see_club_name(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.club.name)
    
    def test_owner_has_admin_options(self):
        self.client.login(username=self.jane.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Club Administration")
        self.assertContains(response, "Manage Club")
        self.assertContains(response, "Club Settings")

    def test_mod_has_no_admin_options(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Club Administration")
        self.assertNotContains(response, "Manage Club")
        self.assertNotContains(response, "Club Settings")
    
    def test_member_has_no_admin_options(self):
        self.client.login(username=self.jack.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Club Administration")
        self.assertNotContains(response, "Manage Club")
        self.assertNotContains(response, "Club Settings")

    def test_can_see_owner(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.owner.username)
        self.assertContains(response, self.owner.public_bio)

    def test_can_see_mods(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        for mod in self.moderators:
            self.assertContains(response, mod.username)
            self.assertContains(response, mod.public_bio)

    def test_can_see_members(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        for member in self.members:
            self.assertContains(response, member.username)
            self.assertContains(response, member.public_bio)

    def test_cannot_see_applicants(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        for applicant in self.applicants:
            self.assertNotContains(response, applicant.username)
            self.assertNotContains(response, applicant.public_bio)

    def test_owner_can_see_delete_club_button(self):
        self.client.login(username=self.jane.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Delete Club")
        
    def test_mod_cannot_see_delete_button(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Delete Club")

    def test_member_cannot_see_delete_button(self):
        self.client.login(username=self.jack.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Delete Club")

    def test_applicant_cannot_see_delete_button(self):
        self.client.login(username=self.applicants[0].username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Delete Club")
    