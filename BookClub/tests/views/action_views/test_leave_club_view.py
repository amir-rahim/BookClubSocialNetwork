"""Tests of the Leave Club view."""
from django.test import TestCase
from django.urls import reverse
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from BookClub.tests.helpers import LogInTester
from BookClub.models import User, Club, ClubMembership


class LeaveClubViewTestCase(TestCase, LogInTester):
    """Tests of the Leave Club view."""

    fixtures = [
            'BookClub/tests/fixtures/default_users.json',
            'BookClub/tests/fixtures/default_clubs.json',
        ]

    def setUp(self):
        self.owner = User.objects.get(pk=1)
        self.moderator = User.objects.get(pk=2)
        self.member = User.objects.get(pk=3)
        self.applicant = User.objects.get(pk=4)
        self.club = Club.objects.get(pk="1")
        self.wrong_club = Club.objects.get(pk="2")

        ClubMembership.objects.create(user=self.owner, club=self.club, membership=ClubMembership.UserRoles.OWNER)
        ClubMembership.objects.create(user=self.moderator, club=self.club, membership=ClubMembership.UserRoles.MODERATOR)
        ClubMembership.objects.create(user=self.member, club=self.club, membership=ClubMembership.UserRoles.MEMBER)
        ClubMembership.objects.create(user=self.applicant, club=self.club, membership=ClubMembership.UserRoles.APPLICANT)

        self.url = reverse('leave_club', kwargs={'url_name': self.club.url_name})

    def test_url(self):
        self.assertEqual(self.url,f'/leave_club/{self.club.url_name}/')

    def test_redirect_when_not_logged_in(self):
        self.assertFalse(self._is_logged_in())
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_get_leave_club_redirects_to_my_club_memberships(self):
        """Test for redirecting user to my_club_memberships when used get method."""

        self.client.login(username=self.member.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        response = self.client.get(reverse('leave_club', kwargs={'url_name': self.club.url_name}))
        redirect_url = reverse('my_club_memberships')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)


    # Tests for successfully leaving a club
    def test_member_can_leave_club(self):
        self.client.login(username=self.member.username, password='Password123')
        before_count = ClubMembership.objects.count()
        response = self.client.post(self.url)
        response_message = self.client.get(reverse('my_club_memberships'))
        messages_list = list(response_message.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.SUCCESS)
        url = reverse('my_club_memberships')
        self.assertRedirects(response, url, status_code=302, target_status_code=200)
        after_count = ClubMembership.objects.count()
        self.assertEqual(before_count, after_count + 1)
        with self.assertRaises(ObjectDoesNotExist):
            ClubMembership.objects.get(user=self.member, club=self.club)

    def test_moderator_can_leave_club(self):
        self.client.login(username=self.moderator.username, password='Password123')
        before_count = ClubMembership.objects.count()
        response = self.client.post(self.url)
        response_message = self.client.get(reverse('my_club_memberships'))
        messages_list = list(response_message.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.SUCCESS)
        url = reverse('my_club_memberships')
        self.assertRedirects(response, url, status_code=302, target_status_code=200)
        after_count = ClubMembership.objects.count()
        self.assertEqual(before_count, after_count + 1)
        with self.assertRaises(ObjectDoesNotExist):
            ClubMembership.objects.get(user=self.moderator, club=self.club)


    # Tests for not being able to leave a club
    def test_owner_cannot_leave_club(self):
        self.client.login(username=self.owner.username, password='Password123')
        before_count = ClubMembership.objects.count()
        response = self.client.post(self.url)
        response_message = self.client.get(reverse('my_club_memberships'))
        messages_list = list(response_message.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        url = reverse('my_club_memberships')
        self.assertRedirects(response, url, status_code=302, target_status_code=200)
        after_count = ClubMembership.objects.count()
        self.assertEqual(before_count, after_count)
        self.assertTrue(ClubMembership.objects.filter(user=self.owner, club=self.club).exists())

    def test_applicant_cannot_leave_club(self):
        self.client.login(username=self.applicant.username, password='Password123')
        before_count = ClubMembership.objects.count()
        response = self.client.post(self.url)
        response_message = self.client.get(reverse('my_club_memberships'))
        messages_list = list(response_message.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        url = reverse('my_club_memberships')
        self.assertRedirects(response, url, status_code=302, target_status_code=200)
        after_count = ClubMembership.objects.count()
        self.assertEqual(before_count, after_count)
        self.assertTrue(ClubMembership.objects.filter(user=self.applicant, club=self.club).exists())


    # Tests for user leaving a club they're not in
    def test_member_leave_wrong_club(self):
        self.client.login(username=self.member.username, password='Password123')
        self.url = reverse('leave_club', kwargs={'url_name': self.wrong_club.url_name})
        before_count = ClubMembership.objects.count()
        response = self.client.post(self.url)
        after_count = ClubMembership.objects.count()
        self.assertEqual(before_count, after_count)

    def test_moderator_leave_wrong_club(self):
        self.client.login(username=self.moderator.username, password='Password123')
        self.url = reverse('leave_club', kwargs={'url_name': self.wrong_club.url_name})
        before_count = ClubMembership.objects.count()
        response = self.client.post(self.url)
        after_count = ClubMembership.objects.count()
        self.assertEqual(before_count, after_count)

    def test_owner_leave_wrong_club(self):
        self.client.login(username=self.owner.username, password='Password123')
        self.url = reverse('leave_club', kwargs={'url_name': self.wrong_club.url_name})
        before_count = ClubMembership.objects.count()
        response = self.client.post(self.url)
        after_count = ClubMembership.objects.count()
        self.assertEqual(before_count, after_count)

    def test_applicant_leave_wrong_club(self):
        self.client.login(username=self.applicant.username, password='Password123')
        self.url = reverse('leave_club', kwargs={'url_name': self.wrong_club.url_name})
        before_count = ClubMembership.objects.count()
        response = self.client.post(self.url)
        after_count = ClubMembership.objects.count()
        self.assertEqual(before_count, after_count)


    # Test for user leaving an invalid club
    def test_member_leave_invalid_club(self):
        self.client.login(username=self.member.username, password='Password123')
        response = self.client.post(reverse('leave_club', kwargs={'url_name': "wrong"}))
        with self.assertRaises(ObjectDoesNotExist):
            Club.objects.get(url_name = "wrong").exists()
        response_message = self.client.get(reverse('my_club_memberships'))
        messages_list = list(response_message.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

    def test_moderator_leave_invalid_club(self):
        self.client.login(username=self.moderator.username, password='Password123')
        response = self.client.post(reverse('leave_club', kwargs={'url_name': "wrong"}))
        with self.assertRaises(ObjectDoesNotExist):
            Club.objects.get(url_name = "wrong").exists()
        response_message = self.client.get(reverse('my_club_memberships'))
        messages_list = list(response_message.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

    def test_owner_leave_invalid_club(self):
        self.client.login(username=self.owner.username, password='Password123')
        response = self.client.post(reverse('leave_club', kwargs={'url_name': "wrong"}))
        with self.assertRaises(ObjectDoesNotExist):
            Club.objects.get(url_name = "wrong").exists()
        response_message = self.client.get(reverse('my_club_memberships'))
        messages_list = list(response_message.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

    def test_applicant_leave_invalid_club(self):
        self.client.login(username=self.applicant.username, password='Password123')
        response = self.client.post(reverse('leave_club', kwargs={'url_name': "wrong"}))
        with self.assertRaises(ObjectDoesNotExist):
            Club.objects.get(url_name = "wrong").exists()
        response_message = self.client.get(reverse('my_club_memberships'))
        messages_list = list(response_message.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
