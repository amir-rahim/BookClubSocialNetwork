"""Tests of the Helper funcitons in BookClub application."""
from django.test import TestCase, tag
from django.urls import reverse

from BookClub import helpers
from BookClub.models import User, Club, ClubMembership

from BookClub.tests.helpers import LogInTester

@tag('helpers')
class HelperFunctionsTestCase(TestCase, LogInTester):

    fixtures =[
        'BookClub/tests/fixtures/default_users.json',
        'BookClub/tests/fixtures/default_clubs.json',
        'BookClub/tests/fixtures/default_club_members.json',
    ]

    def setUp(self):
        self.user2 = User.objects.get(pk=2)
        self.club2 = Club.objects.get(pk=2)

    def test_get_memberships_with_access_returns_empty_if_user_not_logged_in(self):
        home_url = reverse('home')
        response = self.client.get(home_url)
        self.assertEqual(self._is_logged_in(), False)
        memberships_with_access = helpers.get_memberships_with_access(response.wsgi_request.user)
        self.assertEqual(len(memberships_with_access), 0)

    def test_get_memberships_with_access(self):
        self.client.login(username=self.user2.username, password='Password123')
        home_url = reverse('home')
        response = self.client.get(home_url)
        self.assertEqual(self._is_logged_in(), True)
        memberships_with_access = helpers.get_memberships_with_access(response.wsgi_request.user)
        self.assertEqual(len(memberships_with_access), 2)

    def test_has_membership_with_access_for_unauthenticated_user(self):
        home_url = reverse('home')
        response = self.client.get(home_url)
        self.assertEqual(self._is_logged_in(), False)
        return_bool = helpers.has_membership_with_access(self.club2, response.wsgi_request.user)
        self.assertEqual(return_bool, False)

    def test_has_membership_with_access_for_authenticated_owner(self):
        self.client.login(username=self.user2.username, password='Password123')
        home_url = reverse('home')
        response = self.client.get(home_url)
        self.assertEqual(self._is_logged_in(), True)
        return_bool = helpers.has_membership_with_access(self.club2, response.wsgi_request.user)
        self.assertEqual(return_bool, True)
