"""Tests of the apply_to_club view."""
from django.test import TestCase
from django.urls import reverse
from django.contrib.messages import get_messages
from BookClub.models import User, Club, ClubMembership

class ApplyToClubViewTestCase(TestCase):
    """Tests of the apply_to_club view."""

    fixtures = [
        'BookClub/tests/fixtures/default_users.json',
        'BookClub/tests/fixtures/default_clubs.json',
    ]

    def setUp(self):
        self.user = User.objects.get(username="johndoe")
        self.club = Club.objects.get(pk = "1")
        self.url = reverse('join_club', kwargs={'club_id': self.club.id})

    def test_url(self):
        self.assertEqual(self.url,f'/join_club/{self.club.id}')


    # Tests if the user action is on valid/invalid club
    def test_user_joins_or_applies_to_valid_club(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertTrue(Club.objects.filter(pk = self.club.id).exists())
        self.assertTrue(ClubMembership.objects.filter(user=self.user, club=self.club).exists())

    def test_user_joins_or_applies_to_invalid_club(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(reverse('join_club', kwargs={'club_id': self.club.id+9999}))
        self.assertFalse(Club.objects.filter(pk = self.club.id+9999).exists())

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Club does not exist!')


    # Tests if the user has already joined/applied to the club
    def test_user_already_applied_to_private_club(self):
        private_club = Club.objects.get(pk = "3")
        self.client.login(username=self.user.username, password='Password123')
        membership = ClubMembership.objects.create(user=self.user, club=private_club, membership=ClubMembership.UserRoles.APPLICANT)
        membership.save()
        self.assertTrue(ClubMembership.objects.filter(user=self.user, club=private_club, membership=ClubMembership.UserRoles.APPLICANT).exists())
        response = self.client.get(reverse('join_club', kwargs={'club_id': private_club.id}))

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'You have already applied to this club!')

    def test_user_already_club_member(self):
        self.client.login(username=self.user.username, password='Password123')
        membership = ClubMembership.objects.create(user=self.user, club=self.club, membership=ClubMembership.UserRoles.MEMBER)
        membership.save()
        self.assertTrue(ClubMembership.objects.filter(user=self.user, club=self.club, membership=ClubMembership.UserRoles.MEMBER).exists())
        response = self.client.get(reverse('join_club', kwargs={'club_id': self.club.id}))

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'You are already a member of this club!')


    # Tests for users ability to join public clubs and apply to private ones
    def test_user_can_join_public_club(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertTrue(ClubMembership.objects.filter(user=self.user, club=self.club, membership=ClubMembership.UserRoles.MEMBER).exists())

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'You have joined the club!')

    def test_user_can_apply_to_private_club(self):
        private_club = Club.objects.get(pk = "3")
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(reverse('join_club', kwargs={'club_id': private_club.id}))
        self.assertTrue(ClubMembership.objects.filter(user=self.user, club=private_club, membership=ClubMembership.UserRoles.APPLICANT).exists())

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Application to club successful!')
