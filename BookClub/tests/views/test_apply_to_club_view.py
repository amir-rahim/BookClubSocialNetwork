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
        self.url = reverse('apply_to_club', kwargs={'club_id': self.club.id})

    def test_url(self):
        self.assertEqual(self.url,f'/apply_to_club/{self.club.id}')

    def test_user_applies_to_valid_club(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertTrue(ClubMembership.objects.filter(user=self.user, club=self.club).exists())

    def test_user_applies_to_invalid_club(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(reverse('apply_to_club', kwargs={'club_id': self.club.id+9999}))

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Club does not exist!')

    def test_user_already_applied(self):
        self.client.login(username=self.user.username, password='Password123')
        membership = ClubMembership.objects.create(user=self.user, club=self.club, membership=ClubMembership.UserRoles.APPLICANT)
        membership.save()
        response = self.client.get(self.url)

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'You have already applied to this club!')
