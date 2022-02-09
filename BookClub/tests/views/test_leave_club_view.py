"""Tests of the Leave Club view."""
from django.test import TestCase
from django.urls import reverse
from django.contrib.messages import get_messages
from BookClub.models import User, Club, ClubMembership

class LeaveClubViewTestCase(TestCase):
    """Tests of the Leave Club view."""

    fixtures = [
            'BookClub/tests/fixtures/default_users.json',
            'BookClub/tests/fixtures/default_clubs.json',
        ]

    def setUp(self):
        self.user = User.objects.get(username="johndoe")
        self.club = Club.objects.get(pk = "1")
        self.url = reverse('leave_club', kwargs={'club_id': self.club.id})

    def test_url(self):
        self.assertEqual(self.url,f'/leave_club/{self.club.id}')


    def test_user_can_leave_club(self):
        self.client.login(username=self.user.username, password='Password123')
        membership = ClubMembership.objects.create(user=self.user, club=self.club)
        membership.save()
        self.assertTrue(ClubMembership.objects.filter(user=self.user, club=self.club).exists())
        self.client.post(self.url)
        self.assertFalse(ClubMembership.objects.filter(user=self.user, club=self.club).exists())


    def test_user_leaves_valid_club(self):
        self.client.login(username=self.user.username, password='Password123')
        membership = ClubMembership.objects.create(user=self.user, club=self.club)
        membership.save()
        self.client.post(self.url)
        self.assertTrue(Club.objects.filter(pk = self.club.id).exists())
        self.assertFalse(ClubMembership.objects.filter(user=self.user, club=self.club).exists())
