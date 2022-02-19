"""Test approve applicant view."""
from django.test import TestCase, tag
from django.urls import reverse
from BookClub.models import User, Club, ClubMembership
from django.contrib import messages
from BookClub.tests.helpers import LogInTester
from django.core.exceptions import ObjectDoesNotExist


@tag("club", "approveapplicantview")
class ApproveApplicantView(TestCase, LogInTester):
    """Test approve applicant view."""

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

        self.url = reverse('approve_applicant', kwargs={'club_url_name': self.club.club_url_name})

    def test_approve_applicant_url(self):
        self.assertEqual(self.url, f'/approve_applicant/{self.club.club_url_name}/')

    def test_get_approve_applicant_redirects_when_not_logged_in(self):
        """Test for redirecting user when not logged in."""

        self.assertFalse(self._is_logged_in())
        response = self.client.post(self.url, {'user': self.member.username})
        self.assertEqual(response.status_code, 302)

    def test_owner_approve_applicant(self):
        """Test for the owner successfully approving an applicant."""

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
        self.assertTrue(ClubMembership.objects.filter(user=self.applicant, club=self.club,
                                                      membership=ClubMembership.UserRoles.MEMBER).exists())
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_moderator_approve_applicant(self):
        """Test for the moderator successfully approving an applicant."""

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
        self.assertTrue(ClubMembership.objects.filter(user=self.applicant, club=self.club,
                                                      membership=ClubMembership.UserRoles.MEMBER).exists())
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    """Unit tests for user not being able to approve a member"""

    def test_owner_approve_member(self):
        """Test for owner unsuccessfully approving a member."""

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

    def test_moderator_approve_member(self):
        """Test for moderator unsuccessfully approving a member."""

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

    def test_member_approve_another_member(self):
        """Test for another member unsuccessfully approving a member."""

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

    def test_applicant_approve_member(self):
        """Test for applicant unsuccessfully approving a member."""

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

    def test_member_approve_themselves(self):
        """Test for member unsuccessfully approving themselves."""

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

    """Unit tests for user not being able to approve a moderator"""

    def test_owner_approve_moderator(self):
        """Test for owner unsuccessfully approving moderator."""

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

    def test_moderator_approve_another_moderator(self):
        """Test for moderator unsuccessfully approving another moderator."""

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

    def test_member_approve_moderator(self):
        """Test for member unsuccessfully approving moderator."""

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

    def test_applicant_approve_moderator(self):
        """Test for applicant unsuccessfully approving moderator."""

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

    def test_moderator_approve_themselves(self):
        """Test for moderator unsuccessfully approving themselves."""

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

    """Unit tests for user not being able to approve an applicant"""

    def test_member_approve_applicant(self):
        """Test for member unsuccessfully approving applicant."""

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

    def test_applicant_approve_another_applicant(self):
        """Test for applicant unsuccessfully approving another applicant."""

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

    def test_applicant_approve_themselves(self):
        """Test for applicant unsuccessfully approving themselves."""

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

    """Unit tests for user not being able to approve an owner"""

    def test_moderator_approve_owner(self):
        """Test for moderator unsuccessfully approving owner."""

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

    def test_member_approve_owner(self):
        """Test for member unsuccessfully approving owner."""

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

    def test_applicant_approve_owner(self):
        """Test for applicant unsuccessfully approving owner."""

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

    def test_owner_approve_themselves(self):
        """Test for owner unsuccessfully approving themselves."""

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
