"""Unit testing transfer ownership view"""
from django.contrib import messages
from django.test import TestCase, tag
from django.urls import reverse

from BookClub.models import User, Club, ClubMembership
from BookClub.tests.helpers import LogInTester


@tag("views", "action_views", "transfer_ownership")
class TransferOwnerView(TestCase, LogInTester):
    """Transfer ownership view testing"""
    fixtures = [
        'BookClub/tests/fixtures/default_users.json',
        'BookClub/tests/fixtures/default_clubs.json',
    ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.club = Club.objects.get(pk=1)

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

        self.club2 = Club.objects.get(pk=2)
        ClubMembership.objects.create(user=self.applicant, club=self.club2,
                                      membership=ClubMembership.UserRoles.MODERATOR)

        self.url = reverse('transfer_ownership', kwargs={'club_url_name': self.club.club_url_name})

    def test_transfer_ownership_url(self):
        self.assertEqual(self.url, f'/transfer_ownership/{self.club.club_url_name}/')

    def test_transfer_ownership_redirect_not_logged_in(self):
        """Test transferring ownership to any user whilst not logged in"""
        self.assertFalse(self._is_logged_in())

        for user in User.objects.all():
            response = self.client.post(self.url, {"user": user.username})
            self.assertEqual(response.status_code, 302)

    def test_owner_transfer_to_moderator(self):
        """Test for an owner successfully transferring ownership"""
        self.client.login(username=self.owner.username, password="Password123")
        self.assertTrue(self._is_logged_in())
        self.assertTrue(ClubMembership.objects.filter(user=self.owner, club=self.club,
                                                      membership=ClubMembership.UserRoles.OWNER).exists())
        self.assertTrue(ClubMembership.objects.filter(user=self.moderator, club=self.club,
                                                      membership=ClubMembership.UserRoles.MODERATOR).exists())

        response = self.client.post(self.url, {'user': self.moderator.username})
        redirect_url = reverse('member_list', kwargs={'club_url_name': self.club.club_url_name})
        response_message = self.client.get(redirect_url)
        messages_list = list(response_message.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.SUCCESS)

        self.assertTrue(ClubMembership.objects.filter(user=self.moderator, club=self.club,
                                                      membership=ClubMembership.UserRoles.OWNER).exists())
        self.assertTrue(ClubMembership.objects.filter(user=self.owner, club=self.club,
                                                      membership=ClubMembership.UserRoles.MODERATOR).exists())

    def test_another_moderator_transfer_to_moderator(self):
        """Test for another moderator unsuccessfully transferring ownership to a moderator"""
        self.client.login(username=self.moderator.username, password="Password123")
        self.assertTrue(self._is_logged_in())
        self.assertTrue(ClubMembership.objects.filter(user=self.another_moderator, club=self.club).exists())
        self.assertTrue(ClubMembership.objects.filter(user=self.moderator, club=self.club).exists())

        current_user_rank_before = ClubMembership.objects.get(user=self.another_moderator, club=self.club).membership
        self.assertEqual(current_user_rank_before, ClubMembership.UserRoles.MODERATOR)
        target_user_rank_before = ClubMembership.objects.get(user=self.moderator, club=self.club).membership
        self.assertEqual(target_user_rank_before, ClubMembership.UserRoles.MODERATOR)

        response = self.client.post(self.url, {'user': self.moderator.username})
        redirect_url = reverse('member_list', kwargs={'club_url_name': self.club.club_url_name})
        response_message = self.client.get(redirect_url)
        messages_list = list(response_message.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

        current_user_rank_after = ClubMembership.objects.get(user=self.another_moderator, club=self.club).membership
        self.assertTrue(ClubMembership.objects.filter(user=self.another_moderator, club=self.club).exists())
        target_user_rank_after = ClubMembership.objects.get(user=self.moderator, club=self.club).membership
        self.assertTrue(ClubMembership.objects.filter(user=self.moderator, club=self.club).exists())

        self.assertEqual(current_user_rank_before, current_user_rank_after)
        self.assertEqual(target_user_rank_before, target_user_rank_after)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_moderator_transfer_to_themselves(self):
        """Test for a moderator unsuccessfully transferring ownership to themselves"""
        self.client.login(username=self.moderator.username, password="Password123")
        self.assertTrue(self._is_logged_in())
        self.assertTrue(ClubMembership.objects.filter(user=self.moderator, club=self.club).exists())

        current_user_rank_before = ClubMembership.objects.get(user=self.moderator, club=self.club).membership
        self.assertEqual(current_user_rank_before, ClubMembership.UserRoles.MODERATOR)
        target_user_rank_before = ClubMembership.objects.get(user=self.moderator, club=self.club).membership
        self.assertEqual(target_user_rank_before, ClubMembership.UserRoles.MODERATOR)

        response = self.client.post(self.url, {'user': self.moderator.username})
        redirect_url = reverse('member_list', kwargs={'club_url_name': self.club.club_url_name})
        response_message = self.client.get(redirect_url)
        messages_list = list(response_message.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

        current_user_rank_after = ClubMembership.objects.get(user=self.moderator, club=self.club).membership
        self.assertTrue(ClubMembership.objects.filter(user=self.moderator, club=self.club).exists())
        target_user_rank_after = ClubMembership.objects.get(user=self.moderator, club=self.club).membership
        self.assertTrue(ClubMembership.objects.filter(user=self.moderator, club=self.club).exists())

        self.assertEqual(current_user_rank_before, current_user_rank_after)
        self.assertEqual(target_user_rank_before, target_user_rank_after)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_member_transfer_to_moderator(self):
        """Test for a member unsuccessfully transferring ownership to a moderator"""
        self.client.login(username=self.member.username, password="Password123")
        self.assertTrue(self._is_logged_in())
        self.assertTrue(ClubMembership.objects.filter(user=self.member, club=self.club).exists())
        self.assertTrue(ClubMembership.objects.filter(user=self.moderator, club=self.club).exists())

        current_user_rank_before = ClubMembership.objects.get(user=self.member, club=self.club).membership
        self.assertEqual(current_user_rank_before, ClubMembership.UserRoles.MEMBER)
        target_user_rank_before = ClubMembership.objects.get(user=self.moderator, club=self.club).membership
        self.assertEqual(target_user_rank_before, ClubMembership.UserRoles.MODERATOR)

        response = self.client.post(self.url, {'user': self.moderator.username})
        redirect_url = reverse('member_list', kwargs={'club_url_name': self.club.club_url_name})
        response_message = self.client.get(redirect_url)
        messages_list = list(response_message.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

        current_user_rank_after = ClubMembership.objects.get(user=self.member, club=self.club).membership
        self.assertTrue(ClubMembership.objects.filter(user=self.member, club=self.club).exists())
        target_user_rank_after = ClubMembership.objects.get(user=self.moderator, club=self.club).membership
        self.assertTrue(ClubMembership.objects.filter(user=self.moderator, club=self.club).exists())

        self.assertEqual(current_user_rank_before, current_user_rank_after)
        self.assertEqual(target_user_rank_before, target_user_rank_after)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_applicant_transfer_to_moderator(self):
        """Test for an applicant unsuccessfully transferring ownership to a moderator"""
        self.client.login(username=self.applicant.username, password="Password123")
        self.assertTrue(self._is_logged_in())
        self.assertTrue(ClubMembership.objects.filter(user=self.applicant, club=self.club).exists())
        self.assertTrue(ClubMembership.objects.filter(user=self.moderator, club=self.club).exists())

        current_user_rank_before = ClubMembership.objects.get(user=self.applicant, club=self.club).membership
        self.assertEqual(current_user_rank_before, ClubMembership.UserRoles.APPLICANT)
        target_user_rank_before = ClubMembership.objects.get(user=self.moderator, club=self.club).membership
        self.assertEqual(target_user_rank_before, ClubMembership.UserRoles.MODERATOR)

        response = self.client.post(self.url, {'user': self.moderator.username})
        redirect_url = reverse('member_list', kwargs={'club_url_name': self.club.club_url_name})
        response_message = self.client.get(redirect_url)
        messages_list = list(response_message.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

        current_user_rank_after = ClubMembership.objects.get(user=self.applicant, club=self.club).membership
        self.assertTrue(ClubMembership.objects.filter(user=self.applicant, club=self.club).exists())
        target_user_rank_after = ClubMembership.objects.get(user=self.moderator, club=self.club).membership
        self.assertTrue(ClubMembership.objects.filter(user=self.moderator, club=self.club).exists())

        self.assertEqual(current_user_rank_before, current_user_rank_after)
        self.assertEqual(target_user_rank_before, target_user_rank_after)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_owner_transfer_to_member(self):
        """Test for owner unsuccessfully transferring ownership to a member"""
        currentUser = self.owner
        targetUser = self.member

        self.client.login(username=currentUser.username, password="Password123")
        self.assertTrue(self._is_logged_in())
        self.assertTrue(ClubMembership.objects.filter(user=currentUser, club=self.club).exists())
        self.assertTrue(ClubMembership.objects.filter(user=targetUser, club=self.club).exists())

        current_user_rank_before = ClubMembership.objects.get(user=currentUser, club=self.club).membership
        self.assertEqual(current_user_rank_before, ClubMembership.UserRoles.OWNER)
        target_user_rank_before = ClubMembership.objects.get(user=targetUser, club=self.club).membership
        self.assertEqual(target_user_rank_before, ClubMembership.UserRoles.MEMBER)

        response = self.client.post(self.url, {'user': targetUser.username})
        redirect_url = reverse('member_list', kwargs={'club_url_name': self.club.club_url_name})
        response_message = self.client.get(redirect_url)
        messages_list = list(response_message.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

        current_user_rank_after = ClubMembership.objects.get(user=currentUser, club=self.club).membership
        self.assertTrue(ClubMembership.objects.filter(user=currentUser, club=self.club).exists())
        target_user_rank_after = ClubMembership.objects.get(user=targetUser, club=self.club).membership
        self.assertTrue(ClubMembership.objects.filter(user=targetUser, club=self.club).exists())

        self.assertEqual(current_user_rank_before, current_user_rank_after)
        self.assertEqual(target_user_rank_before, target_user_rank_after)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_moderator_transfer_to_member(self):
        """Test for another moderator unsuccessfully transferring ownership to a member"""
        currentUser = self.moderator
        targetUser = self.member

        self.client.login(username=currentUser.username, password="Password123")
        self.assertTrue(self._is_logged_in())
        self.assertTrue(ClubMembership.objects.filter(user=currentUser, club=self.club).exists())
        self.assertTrue(ClubMembership.objects.filter(user=targetUser, club=self.club).exists())

        current_user_rank_before = ClubMembership.objects.get(user=currentUser, club=self.club).membership
        self.assertEqual(current_user_rank_before, ClubMembership.UserRoles.MODERATOR)
        target_user_rank_before = ClubMembership.objects.get(user=targetUser, club=self.club).membership
        self.assertEqual(target_user_rank_before, ClubMembership.UserRoles.MEMBER)

        response = self.client.post(self.url, {'user': targetUser.username})
        redirect_url = reverse('member_list', kwargs={'club_url_name': self.club.club_url_name})
        response_message = self.client.get(redirect_url)
        messages_list = list(response_message.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

        current_user_rank_after = ClubMembership.objects.get(user=currentUser, club=self.club).membership
        self.assertTrue(ClubMembership.objects.filter(user=currentUser, club=self.club).exists())
        target_user_rank_after = ClubMembership.objects.get(user=targetUser, club=self.club).membership
        self.assertTrue(ClubMembership.objects.filter(user=targetUser, club=self.club).exists())

        self.assertEqual(current_user_rank_before, current_user_rank_after)
        self.assertEqual(target_user_rank_before, target_user_rank_after)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_another_member_transfer_to_member(self):
        """Test for another member unsuccessfully transferring ownership to a member"""
        currentUser = self.another_member
        targetUser = self.member

        self.client.login(username=currentUser.username, password="Password123")
        self.assertTrue(self._is_logged_in())
        self.assertTrue(ClubMembership.objects.filter(user=currentUser, club=self.club).exists())
        self.assertTrue(ClubMembership.objects.filter(user=targetUser, club=self.club).exists())

        current_user_rank_before = ClubMembership.objects.get(user=currentUser, club=self.club).membership
        self.assertEqual(current_user_rank_before, ClubMembership.UserRoles.MEMBER)
        target_user_rank_before = ClubMembership.objects.get(user=targetUser, club=self.club).membership
        self.assertEqual(target_user_rank_before, ClubMembership.UserRoles.MEMBER)

        response = self.client.post(self.url, {'user': targetUser.username})
        redirect_url = reverse('member_list', kwargs={'club_url_name': self.club.club_url_name})
        response_message = self.client.get(redirect_url)
        messages_list = list(response_message.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

        current_user_rank_after = ClubMembership.objects.get(user=currentUser, club=self.club).membership
        self.assertTrue(ClubMembership.objects.filter(user=currentUser, club=self.club).exists())
        target_user_rank_after = ClubMembership.objects.get(user=targetUser, club=self.club).membership
        self.assertTrue(ClubMembership.objects.filter(user=targetUser, club=self.club).exists())

        self.assertEqual(current_user_rank_before, current_user_rank_after)
        self.assertEqual(target_user_rank_before, target_user_rank_after)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_member_transfer_to_themselves(self):
        """Test for a member unsuccessfully transferring ownership to themselves"""
        currentUser = self.member
        targetUser = self.member

        self.client.login(username=currentUser.username, password="Password123")
        self.assertTrue(self._is_logged_in())
        self.assertTrue(ClubMembership.objects.filter(user=currentUser, club=self.club).exists())
        self.assertTrue(ClubMembership.objects.filter(user=targetUser, club=self.club).exists())

        current_user_rank_before = ClubMembership.objects.get(user=currentUser, club=self.club).membership
        self.assertEqual(current_user_rank_before, ClubMembership.UserRoles.MEMBER)
        target_user_rank_before = ClubMembership.objects.get(user=targetUser, club=self.club).membership
        self.assertEqual(target_user_rank_before, ClubMembership.UserRoles.MEMBER)

        response = self.client.post(self.url, {'user': targetUser.username})
        redirect_url = reverse('member_list', kwargs={'club_url_name': self.club.club_url_name})
        response_message = self.client.get(redirect_url)
        messages_list = list(response_message.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

        current_user_rank_after = ClubMembership.objects.get(user=currentUser, club=self.club).membership
        self.assertTrue(ClubMembership.objects.filter(user=currentUser, club=self.club).exists())
        target_user_rank_after = ClubMembership.objects.get(user=targetUser, club=self.club).membership
        self.assertTrue(ClubMembership.objects.filter(user=targetUser, club=self.club).exists())

        self.assertEqual(current_user_rank_before, current_user_rank_after)
        self.assertEqual(target_user_rank_before, target_user_rank_after)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_applicant_transfer_to_member(self):
        """Test for an applicant unsuccessfully transferring ownership to a member"""
        currentUser = self.applicant
        targetUser = self.member

        self.client.login(username=currentUser.username, password="Password123")
        self.assertTrue(self._is_logged_in())
        self.assertTrue(ClubMembership.objects.filter(user=currentUser, club=self.club).exists())
        self.assertTrue(ClubMembership.objects.filter(user=targetUser, club=self.club).exists())

        current_user_rank_before = ClubMembership.objects.get(user=currentUser, club=self.club).membership
        self.assertEqual(current_user_rank_before, ClubMembership.UserRoles.APPLICANT)
        target_user_rank_before = ClubMembership.objects.get(user=targetUser, club=self.club).membership
        self.assertEqual(target_user_rank_before, ClubMembership.UserRoles.MEMBER)

        response = self.client.post(self.url, {'user': targetUser.username})
        redirect_url = reverse('member_list', kwargs={'club_url_name': self.club.club_url_name})
        response_message = self.client.get(redirect_url)
        messages_list = list(response_message.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

        current_user_rank_after = ClubMembership.objects.get(user=currentUser, club=self.club).membership
        self.assertTrue(ClubMembership.objects.filter(user=currentUser, club=self.club).exists())
        target_user_rank_after = ClubMembership.objects.get(user=targetUser, club=self.club).membership
        self.assertTrue(ClubMembership.objects.filter(user=targetUser, club=self.club).exists())

        self.assertEqual(current_user_rank_before, current_user_rank_after)
        self.assertEqual(target_user_rank_before, target_user_rank_after)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_owner_transfer_to_applicant(self):
        """Test for an owner unsuccessfully transferring ownership to an applicant"""
        currentUser = self.owner
        targetUser = self.applicant

        self.client.login(username=currentUser.username, password="Password123")
        self.assertTrue(self._is_logged_in())
        self.assertTrue(ClubMembership.objects.filter(user=currentUser, club=self.club).exists())
        self.assertTrue(ClubMembership.objects.filter(user=targetUser, club=self.club).exists())

        current_user_rank_before = ClubMembership.objects.get(user=currentUser, club=self.club).membership
        self.assertEqual(current_user_rank_before, ClubMembership.UserRoles.OWNER)
        target_user_rank_before = ClubMembership.objects.get(user=targetUser, club=self.club).membership
        self.assertEqual(target_user_rank_before, ClubMembership.UserRoles.APPLICANT)

        response = self.client.post(self.url, {'user': targetUser.username})
        redirect_url = reverse('member_list', kwargs={'club_url_name': self.club.club_url_name})
        response_message = self.client.get(redirect_url)
        messages_list = list(response_message.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

        current_user_rank_after = ClubMembership.objects.get(user=currentUser, club=self.club).membership
        self.assertTrue(ClubMembership.objects.filter(user=currentUser, club=self.club).exists())
        target_user_rank_after = ClubMembership.objects.get(user=targetUser, club=self.club).membership
        self.assertTrue(ClubMembership.objects.filter(user=targetUser, club=self.club).exists())

        self.assertEqual(current_user_rank_before, current_user_rank_after)
        self.assertEqual(target_user_rank_before, target_user_rank_after)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_moderator_transfer_to_applicant(self):
        """Test for a moderator unsuccessfully transferring ownership to an applicant"""
        currentUser = self.moderator
        targetUser = self.applicant

        self.client.login(username=currentUser.username, password="Password123")
        self.assertTrue(self._is_logged_in())
        self.assertTrue(ClubMembership.objects.filter(user=currentUser, club=self.club).exists())
        self.assertTrue(ClubMembership.objects.filter(user=targetUser, club=self.club).exists())

        # Checking the ranks before
        current_user_rank_before = ClubMembership.objects.get(user=currentUser, club=self.club).membership
        self.assertEqual(current_user_rank_before, ClubMembership.UserRoles.MODERATOR)
        target_user_rank_before = ClubMembership.objects.get(user=targetUser, club=self.club).membership
        self.assertEqual(target_user_rank_before, ClubMembership.UserRoles.APPLICANT)

        response = self.client.post(self.url, {'user': targetUser.username})
        redirect_url = reverse('member_list', kwargs={'club_url_name': self.club.club_url_name})
        response_message = self.client.get(redirect_url)
        messages_list = list(response_message.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

        # Checking the ranks after
        current_user_rank_after = ClubMembership.objects.get(user=currentUser, club=self.club).membership
        self.assertTrue(ClubMembership.objects.filter(user=currentUser, club=self.club).exists())
        target_user_rank_after = ClubMembership.objects.get(user=targetUser, club=self.club).membership
        self.assertTrue(ClubMembership.objects.filter(user=targetUser, club=self.club).exists())

        self.assertEqual(current_user_rank_before, current_user_rank_after)
        self.assertEqual(target_user_rank_before, target_user_rank_after)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_member_transfer_to_applicant(self):
        """Test for a member unsuccessfully transferring ownership to an applicant"""
        currentUser = self.member
        targetUser = self.applicant

        self.client.login(username=currentUser.username, password="Password123")
        self.assertTrue(self._is_logged_in())
        self.assertTrue(ClubMembership.objects.filter(user=currentUser, club=self.club).exists())
        self.assertTrue(ClubMembership.objects.filter(user=targetUser, club=self.club).exists())

        # Checking the ranks before
        current_user_rank_before = ClubMembership.objects.get(user=currentUser, club=self.club).membership
        self.assertEqual(current_user_rank_before, ClubMembership.UserRoles.MEMBER)
        target_user_rank_before = ClubMembership.objects.get(user=targetUser, club=self.club).membership
        self.assertEqual(target_user_rank_before, ClubMembership.UserRoles.APPLICANT)

        response = self.client.post(self.url, {'user': targetUser.username})
        redirect_url = reverse('member_list', kwargs={'club_url_name': self.club.club_url_name})
        response_message = self.client.get(redirect_url)
        messages_list = list(response_message.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

        # Checking the ranks after
        current_user_rank_after = ClubMembership.objects.get(user=currentUser, club=self.club).membership
        self.assertTrue(ClubMembership.objects.filter(user=currentUser, club=self.club).exists())
        target_user_rank_after = ClubMembership.objects.get(user=targetUser, club=self.club).membership
        self.assertTrue(ClubMembership.objects.filter(user=targetUser, club=self.club).exists())

        self.assertEqual(current_user_rank_before, current_user_rank_after)
        self.assertEqual(target_user_rank_before, target_user_rank_after)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_another_applicant_transfer_to_applicant(self):
        """Test for another applicant unsuccessfully transferring ownership to an applicant"""
        currentUser = self.another_applicant
        targetUser = self.applicant

        self.client.login(username=currentUser.username, password="Password123")
        self.assertTrue(self._is_logged_in())
        self.assertTrue(ClubMembership.objects.filter(user=currentUser, club=self.club).exists())
        self.assertTrue(ClubMembership.objects.filter(user=targetUser, club=self.club).exists())

        # Checking the ranks before
        current_user_rank_before = ClubMembership.objects.get(user=currentUser, club=self.club).membership
        self.assertEqual(current_user_rank_before, ClubMembership.UserRoles.APPLICANT)
        target_user_rank_before = ClubMembership.objects.get(user=targetUser, club=self.club).membership
        self.assertEqual(target_user_rank_before, ClubMembership.UserRoles.APPLICANT)

        response = self.client.post(self.url, {'user': targetUser.username})
        redirect_url = reverse('member_list', kwargs={'club_url_name': self.club.club_url_name})
        response_message = self.client.get(redirect_url)
        messages_list = list(response_message.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

        # Checking the ranks after
        current_user_rank_after = ClubMembership.objects.get(user=currentUser, club=self.club).membership
        self.assertTrue(ClubMembership.objects.filter(user=currentUser, club=self.club).exists())
        target_user_rank_after = ClubMembership.objects.get(user=targetUser, club=self.club).membership
        self.assertTrue(ClubMembership.objects.filter(user=targetUser, club=self.club).exists())

        self.assertEqual(current_user_rank_before, current_user_rank_after)
        self.assertEqual(target_user_rank_before, target_user_rank_after)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_applicant_transfer_to_themselves(self):
        """Test for an applicant unsuccessfully transferring ownership to themselves"""
        currentUser = self.applicant
        targetUser = self.applicant

        self.client.login(username=currentUser.username, password="Password123")
        self.assertTrue(self._is_logged_in())
        self.assertTrue(ClubMembership.objects.filter(user=currentUser, club=self.club).exists())
        self.assertTrue(ClubMembership.objects.filter(user=targetUser, club=self.club).exists())

        # Checking the ranks before
        current_user_rank_before = ClubMembership.objects.get(user=currentUser, club=self.club).membership
        self.assertEqual(current_user_rank_before, ClubMembership.UserRoles.APPLICANT)
        target_user_rank_before = ClubMembership.objects.get(user=targetUser, club=self.club).membership
        self.assertEqual(target_user_rank_before, ClubMembership.UserRoles.APPLICANT)

        response = self.client.post(self.url, {'user': targetUser.username})
        redirect_url = reverse('member_list', kwargs={'club_url_name': self.club.club_url_name})
        response_message = self.client.get(redirect_url)
        messages_list = list(response_message.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

        # Checking the ranks after
        current_user_rank_after = ClubMembership.objects.get(user=currentUser, club=self.club).membership
        self.assertTrue(ClubMembership.objects.filter(user=currentUser, club=self.club).exists())
        target_user_rank_after = ClubMembership.objects.get(user=targetUser, club=self.club).membership
        self.assertTrue(ClubMembership.objects.filter(user=targetUser, club=self.club).exists())

        self.assertEqual(current_user_rank_before, current_user_rank_after)
        self.assertEqual(target_user_rank_before, target_user_rank_after)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_owner_transfer_to_themselves(self):
        """Test for an owner unsuccessfully transferring ownership to themselves"""
        currentUser = self.owner
        targetUser = self.owner

        self.client.login(username=currentUser.username, password="Password123")
        self.assertTrue(self._is_logged_in())
        self.assertTrue(ClubMembership.objects.filter(user=currentUser, club=self.club).exists())
        self.assertTrue(ClubMembership.objects.filter(user=targetUser, club=self.club).exists())

        # Checking the ranks before
        current_user_rank_before = ClubMembership.objects.get(user=currentUser, club=self.club).membership
        self.assertEqual(current_user_rank_before, ClubMembership.UserRoles.OWNER)
        target_user_rank_before = ClubMembership.objects.get(user=targetUser, club=self.club).membership
        self.assertEqual(target_user_rank_before, ClubMembership.UserRoles.OWNER)

        response = self.client.post(self.url, {'user': targetUser.username})
        redirect_url = reverse('member_list', kwargs={'club_url_name': self.club.club_url_name})
        response_message = self.client.get(redirect_url)
        messages_list = list(response_message.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

        # Checking the ranks after
        current_user_rank_after = ClubMembership.objects.get(user=currentUser, club=self.club).membership
        self.assertTrue(ClubMembership.objects.filter(user=currentUser, club=self.club).exists())
        target_user_rank_after = ClubMembership.objects.get(user=targetUser, club=self.club).membership
        self.assertTrue(ClubMembership.objects.filter(user=targetUser, club=self.club).exists())

        self.assertEqual(current_user_rank_before, current_user_rank_after)
        self.assertEqual(target_user_rank_before, target_user_rank_after)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_owner_transfer_to_wrong_moderator(self):
        """Test for an owner unsuccessfully transferring ownership to the wrong moderator"""
        currentUser = self.owner
        targetUser = self.applicant # Using applicant here as they are the moderator of club 2

        self.client.login(username=currentUser.username, password="Password123")
        self.assertTrue(self._is_logged_in())
        self.assertTrue(ClubMembership.objects.filter(user=currentUser, club=self.club).exists())
        self.assertTrue(ClubMembership.objects.filter(user=targetUser, club=self.club2).exists())

        # Checking that the users are not in the same club
        self.assertFalse(
            ClubMembership.objects.get(user=currentUser, club=self.club).club == ClubMembership.objects.get(
                user=targetUser, club=self.club2).club)

        # Checking the ranks before
        current_user_rank_before = ClubMembership.objects.get(user=currentUser, club=self.club).membership
        self.assertEqual(current_user_rank_before, ClubMembership.UserRoles.OWNER)
        target_user_rank_before = ClubMembership.objects.get(user=targetUser, club=self.club2).membership
        self.assertEqual(target_user_rank_before, ClubMembership.UserRoles.MODERATOR)

        response = self.client.post(self.url, {'user': targetUser.username})
        redirect_url = reverse('member_list', kwargs={'club_url_name': self.club.club_url_name})
        response_message = self.client.get(redirect_url)
        messages_list = list(response_message.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

        # Checking the ranks after
        current_user_rank_after = ClubMembership.objects.get(user=currentUser, club=self.club).membership
        self.assertTrue(ClubMembership.objects.filter(user=currentUser, club=self.club).exists())
        target_user_rank_after = ClubMembership.objects.get(user=targetUser, club=self.club2).membership
        self.assertTrue(ClubMembership.objects.filter(user=targetUser, club=self.club2).exists())

        self.assertEqual(current_user_rank_before, current_user_rank_after)
        self.assertEqual(target_user_rank_before, target_user_rank_after)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
