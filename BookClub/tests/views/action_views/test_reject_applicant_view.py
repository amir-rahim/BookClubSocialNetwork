"""Test reject applicant view."""
from django.contrib import messages
from django.test import TestCase, tag
from django.urls import reverse

from BookClub.models import User, Club, ClubMembership
from BookClub.tests.helpers import LogInTester


@tag("views", "action_views", "reject_applicant")
class RejectApplicantView(TestCase, LogInTester):
    """Test reject applicant view."""

    fixtures = [
        'BookClub/tests/fixtures/default_users.json',
        'BookClub/tests/fixtures/default_clubs.json',
    ]

    def setUp(self):
        self.owner = User.objects.get(pk=1)
        self.moderator = User.objects.get(pk=2)
        self.another_moderator = User.objects.get(pk=3)
        self.member = User.objects.get(pk=4)
        self.another_member = User.objects.get(pk=5)
        self.applicant = User.objects.get(pk=6)
        self.another_applicant = User.objects.get(pk=7)

        self.club = Club.objects.get(pk=1)
        ClubMembership.objects.create(user=self.owner, club=self.club, membership=ClubMembership.UserRoles.OWNER)
        ClubMembership.objects.create(user=self.moderator, club=self.club,
                                      membership=ClubMembership.UserRoles.MODERATOR)
        ClubMembership.objects.create(user=self.another_moderator, club=self.club,
                                      membership=ClubMembership.UserRoles.MODERATOR)
        ClubMembership.objects.create(user=self.member, club=self.club, membership=ClubMembership.UserRoles.MEMBER)
        ClubMembership.objects.create(user=self.another_member, club=self.club,
                                      membership=ClubMembership.UserRoles.MEMBER)
        ClubMembership.objects.create(user=self.applicant, club=self.club,
                                      membership=ClubMembership.UserRoles.APPLICANT)
        ClubMembership.objects.create(user=self.another_applicant, club=self.club,
                                      membership=ClubMembership.UserRoles.APPLICANT)

        self.url = reverse('reject_applicant', kwargs={'club_url_name': self.club.club_url_name})

    def test_reject_applicant_url(self):
        self.assertEqual(self.url, f'/reject_applicant/{self.club.club_url_name}/')

    def test_get_reject_applicant_redirects_when_not_logged_in(self):
        """Test for redirecting user when not logged in."""

        self.assertFalse(self._is_logged_in())
        response = self.client.post(self.url, {'user': self.member.username})
        self.assertEqual(response.status_code, 302)

    def test_owner_reject_applicant(self):
        """Test for the owner successfully rejecting an applicant."""

        self.client.login(username=self.owner.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        self.assertTrue(ClubMembership.objects.filter(user=self.applicant, club=self.club,
                                                      membership=ClubMembership.UserRoles.APPLICANT).exists())
        response = self.client.post(self.url, {'user': self.applicant.username})
        redirect_url = reverse('applicant_list', kwargs={'club_url_name': self.club.club_url_name})
        response_message = self.client.get(redirect_url)
        messages_list = list(response_message.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.SUCCESS)
        self.assertFalse(ClubMembership.objects.filter(user=self.applicant, club=self.club,
                                                      membership=ClubMembership.UserRoles.MEMBER).exists())
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_moderator_reject_applicant(self):
        """Test for the moderator successfully rejecting an applicant."""

        self.client.login(username=self.moderator.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        self.assertTrue(ClubMembership.objects.filter(user=self.applicant, club=self.club,
                                                      membership=ClubMembership.UserRoles.APPLICANT).exists())
        response = self.client.post(self.url, {'user': self.applicant.username})
        redirect_url = reverse('applicant_list', kwargs={'club_url_name': self.club.club_url_name})
        response_message = self.client.get(redirect_url)
        messages_list = list(response_message.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.SUCCESS)
        self.assertFalse(ClubMembership.objects.filter(user=self.applicant, club=self.club,
                                                      membership=ClubMembership.UserRoles.MEMBER).exists())
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    """Unit tests for user not being able to reject a member"""

    def test_owner_reject_member(self):
        """Test for owner unsuccessfully rejecting a member."""

        self.client.login(username=self.owner.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        self.assertTrue(ClubMembership.objects.filter(user=self.member, club=self.club,
                                                      membership=ClubMembership.UserRoles.MEMBER).exists())
        response = self.client.post(self.url, {'user': self.member.username})
        redirect_url = reverse('applicant_list', kwargs={'club_url_name': self.club.club_url_name})
        response_message = self.client.get(redirect_url)
        messages_list = list(response_message.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        self.assertTrue(ClubMembership.objects.filter(user=self.member, club=self.club,
                                                      membership=ClubMembership.UserRoles.MEMBER).exists())
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_moderator_reject_member(self):
        """Test for moderator unsuccessfully rejecting a member."""

        self.client.login(username=self.moderator.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        self.assertTrue(ClubMembership.objects.filter(user=self.member, club=self.club,
                                                      membership=ClubMembership.UserRoles.MEMBER).exists())
        response = self.client.post(self.url, {'user': self.member.username})
        redirect_url = reverse('applicant_list', kwargs={'club_url_name': self.club.club_url_name})
        response_message = self.client.get(redirect_url)
        messages_list = list(response_message.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        self.assertTrue(ClubMembership.objects.filter(user=self.member, club=self.club,
                                                      membership=ClubMembership.UserRoles.MEMBER).exists())
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_member_reject_another_member(self):
        """Test for another member unsuccessfully rejecting a member."""

        self.client.login(username=self.member.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        self.assertTrue(ClubMembership.objects.filter(user=self.another_member, club=self.club,
                                                      membership=ClubMembership.UserRoles.MEMBER).exists())
        response = self.client.post(self.url, {'user': self.another_member.username})
        redirect_url = reverse('home')
        response_message = self.client.get(redirect_url)
        messages_list = list(response_message.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        self.assertTrue(ClubMembership.objects.filter(user=self.another_member, club=self.club,
                                                      membership=ClubMembership.UserRoles.MEMBER).exists())
        self.assertEqual(response.status_code, 302)

    def test_applicant_reject_member(self):
        """Test for applicant unsuccessfully rejecting a member."""

        self.client.login(username=self.applicant.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        self.assertTrue(ClubMembership.objects.filter(user=self.member, club=self.club,
                                                      membership=ClubMembership.UserRoles.MEMBER).exists())
        response = self.client.post(self.url, {'user': self.member.username})
        redirect_url = reverse('home')
        response_message = self.client.get(redirect_url)
        messages_list = list(response_message.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        self.assertTrue(ClubMembership.objects.filter(user=self.member, club=self.club,
                                                      membership=ClubMembership.UserRoles.MEMBER).exists())
        self.assertEqual(response.status_code, 302)

    def test_member_reject_themselves(self):
        """Test for member unsuccessfully rejecting themselves."""

        self.client.login(username=self.member.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        self.assertTrue(ClubMembership.objects.filter(user=self.member, club=self.club,
                                                      membership=ClubMembership.UserRoles.MEMBER).exists())
        response = self.client.post(self.url, {'user': self.member.username})
        redirect_url = reverse('home')
        response_message = self.client.get(redirect_url)
        messages_list = list(response_message.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        self.assertTrue(ClubMembership.objects.filter(user=self.member, club=self.club,
                                                      membership=ClubMembership.UserRoles.MEMBER).exists())
        self.assertEqual(response.status_code, 302)

    """Unit tests for user not being able to reject a moderator"""

    def test_owner_reject_moderator(self):
        """Test for owner unsuccessfully rejecting moderator."""

        self.client.login(username=self.owner.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        self.assertTrue(ClubMembership.objects.filter(user=self.moderator, club=self.club,
                                                      membership=ClubMembership.UserRoles.MODERATOR).exists())
        response = self.client.post(self.url, {'user': self.moderator.username})
        redirect_url = reverse('applicant_list', kwargs={'club_url_name': self.club.club_url_name})
        response_message = self.client.get(redirect_url)
        messages_list = list(response_message.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        self.assertTrue(ClubMembership.objects.filter(user=self.moderator, club=self.club,
                                                      membership=ClubMembership.UserRoles.MODERATOR).exists())
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_moderator_reject_another_moderator(self):
        """Test for moderator unsuccessfully rejecting another moderator."""

        self.client.login(username=self.another_moderator.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        self.assertTrue(ClubMembership.objects.filter(user=self.moderator, club=self.club,
                                                      membership=ClubMembership.UserRoles.MODERATOR).exists())
        response = self.client.post(self.url, {'user': self.moderator.username})
        redirect_url = reverse('applicant_list', kwargs={'club_url_name': self.club.club_url_name})
        response_message = self.client.get(redirect_url)
        messages_list = list(response_message.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        self.assertTrue(ClubMembership.objects.filter(user=self.moderator, club=self.club,
                                                      membership=ClubMembership.UserRoles.MODERATOR).exists())
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_member_reject_moderator(self):
        """Test for member unsuccessfully rejecting moderator."""

        self.client.login(username=self.member.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        self.assertTrue(ClubMembership.objects.filter(user=self.moderator, club=self.club,
                                                      membership=ClubMembership.UserRoles.MODERATOR).exists())
        response = self.client.post(self.url, {'user': self.moderator.username})
        redirect_url = reverse('home')
        response_message = self.client.get(redirect_url)
        messages_list = list(response_message.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        self.assertTrue(ClubMembership.objects.filter(user=self.moderator, club=self.club,
                                                      membership=ClubMembership.UserRoles.MODERATOR).exists())
        self.assertEqual(response.status_code, 302)

    def test_applicant_reject_moderator(self):
        """Test for applicant unsuccessfully rejecting moderator."""

        self.client.login(username=self.applicant.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        self.assertTrue(ClubMembership.objects.filter(user=self.moderator, club=self.club,
                                                      membership=ClubMembership.UserRoles.MODERATOR).exists())
        response = self.client.post(self.url, {'user': self.moderator.username})
        redirect_url = reverse('home')
        response_message = self.client.get(redirect_url)
        messages_list = list(response_message.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        self.assertTrue(ClubMembership.objects.filter(user=self.moderator, club=self.club,
                                                      membership=ClubMembership.UserRoles.MODERATOR).exists())
        self.assertEqual(response.status_code, 302)

    def test_moderator_reject_themselves(self):
        """Test for moderator unsuccessfully rejecting themselves."""

        self.client.login(username=self.moderator.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        self.assertTrue(ClubMembership.objects.filter(user=self.moderator, club=self.club,
                                                      membership=ClubMembership.UserRoles.MODERATOR).exists())
        response = self.client.post(self.url, {'user': self.moderator.username})
        redirect_url = reverse('applicant_list', kwargs={'club_url_name': self.club.club_url_name})
        response_message = self.client.get(redirect_url)
        messages_list = list(response_message.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        self.assertTrue(ClubMembership.objects.filter(user=self.moderator, club=self.club,
                                                      membership=ClubMembership.UserRoles.MODERATOR).exists())
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    """Unit tests for user not being able to reject an applicant"""

    def test_member_reject_applicant(self):
        """Test for member unsuccessfully rejecting applicant."""

        self.client.login(username=self.member.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        self.assertTrue(ClubMembership.objects.filter(user=self.applicant, club=self.club,
                                                      membership=ClubMembership.UserRoles.APPLICANT).exists())
        response = self.client.post(self.url, {'user': self.applicant.username})
        redirect_url = reverse('home')
        response_message = self.client.get(redirect_url)
        messages_list = list(response_message.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        self.assertTrue(ClubMembership.objects.filter(user=self.applicant, club=self.club,
                                                      membership=ClubMembership.UserRoles.APPLICANT).exists())
        self.assertEqual(response.status_code, 302)

    def test_applicant_reject_another_applicant(self):
        """Test for applicant unsuccessfully rejecting another applicant."""

        self.client.login(username=self.another_applicant.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        self.assertTrue(ClubMembership.objects.filter(user=self.applicant, club=self.club,
                                                      membership=ClubMembership.UserRoles.APPLICANT).exists())
        response = self.client.post(self.url, {'user': self.applicant.username})
        redirect_url = reverse('home')
        response_message = self.client.get(redirect_url)
        messages_list = list(response_message.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        self.assertTrue(ClubMembership.objects.filter(user=self.applicant, club=self.club,
                                                      membership=ClubMembership.UserRoles.APPLICANT).exists())
        self.assertEqual(response.status_code, 302)

    def test_applicant_reject_themselves(self):
        """Test for applicant unsuccessfully rejecting themselves."""

        self.client.login(username=self.applicant.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        self.assertTrue(ClubMembership.objects.filter(user=self.applicant, club=self.club,
                                                      membership=ClubMembership.UserRoles.APPLICANT).exists())
        response = self.client.post(self.url, {'user': self.applicant.username})
        redirect_url = reverse('home')
        response_message = self.client.get(redirect_url)
        messages_list = list(response_message.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        self.assertTrue(ClubMembership.objects.filter(user=self.applicant, club=self.club,
                                                      membership=ClubMembership.UserRoles.APPLICANT).exists())
        self.assertEqual(response.status_code, 302)

    """Unit tests for user not being able to reject an owner"""

    def test_moderator_reject_owner(self):
        """Test for moderator unsuccessfully rejecting owner."""

        self.client.login(username=self.moderator.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        self.assertTrue(ClubMembership.objects.filter(user=self.owner, club=self.club,
                                                      membership=ClubMembership.UserRoles.OWNER).exists())
        response = self.client.post(self.url, {'user': self.owner.username})
        redirect_url = reverse('applicant_list', kwargs={'club_url_name': self.club.club_url_name})
        response_message = self.client.get(redirect_url)
        messages_list = list(response_message.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        self.assertTrue(ClubMembership.objects.filter(user=self.owner, club=self.club,
                                                      membership=ClubMembership.UserRoles.OWNER).exists())
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_member_reject_owner(self):
        """Test for member unsuccessfully rejecting owner."""

        self.client.login(username=self.member.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        self.assertTrue(ClubMembership.objects.filter(user=self.owner, club=self.club,
                                                      membership=ClubMembership.UserRoles.OWNER).exists())
        response = self.client.post(self.url, {'user': self.owner.username})
        redirect_url = reverse('home')
        response_message = self.client.get(redirect_url)
        messages_list = list(response_message.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        self.assertTrue(ClubMembership.objects.filter(user=self.owner, club=self.club,
                                                      membership=ClubMembership.UserRoles.OWNER).exists())
        self.assertEqual(response.status_code, 302)

    def test_applicant_reject_owner(self):
        """Test for applicant unsuccessfully rejecting owner."""

        self.client.login(username=self.applicant.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        self.assertTrue(ClubMembership.objects.filter(user=self.owner, club=self.club,
                                                      membership=ClubMembership.UserRoles.OWNER).exists())
        response = self.client.post(self.url, {'user': self.owner.username})
        redirect_url = reverse('home')
        response_message = self.client.get(redirect_url)
        messages_list = list(response_message.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        self.assertTrue(ClubMembership.objects.filter(user=self.owner, club=self.club,
                                                      membership=ClubMembership.UserRoles.OWNER).exists())
        self.assertEqual(response.status_code, 302)

    def test_owner_reject_themselves(self):
        """Test for owner unsuccessfully rejecting themselves."""

        self.client.login(username=self.owner.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        self.assertTrue(ClubMembership.objects.filter(user=self.owner, club=self.club,
                                                      membership=ClubMembership.UserRoles.OWNER).exists())
        response = self.client.post(self.url, {'user': self.owner.username})
        redirect_url = reverse('applicant_list', kwargs={'club_url_name': self.club.club_url_name})
        response_message = self.client.get(redirect_url)
        messages_list = list(response_message.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        self.assertTrue(ClubMembership.objects.filter(user=self.owner, club=self.club,
                                                      membership=ClubMembership.UserRoles.OWNER).exists())
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
