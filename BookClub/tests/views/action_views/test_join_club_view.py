"""Tests of the Join Club view."""
from django.test import TestCase
from django.urls import reverse
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from BookClub.tests.helpers import LogInTester
from BookClub.models import User, Club, ClubMembership

class JoinClubViewTestCase(TestCase, LogInTester):
    """Tests of the Join Club view."""

    fixtures = [
        'BookClub/tests/fixtures/default_users.json',
        'BookClub/tests/fixtures/default_clubs.json',
    ]

    def setUp(self):
        self.user = User.objects.get(username="johndoe")
        self.public_club = Club.objects.get(pk = "1")
        self.private_club = Club.objects.get(pk = "3")
        self.url = reverse('join_club', kwargs={'url_name': self.public_club.url_name})

    def test_url(self):
        self.assertEqual(self.url,f'/join_club/{self.public_club.url_name}/')

    def test_redirect_when_not_logged_in(self):
        self.assertFalse(self._is_logged_in())
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_get_join_club_redirects_to_available_clubs(self):
        """Test for redirecting user to available_clubs when used get method."""

        self.client.login(username=self.user.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        response = self.client.get(reverse('join_club', kwargs={'url_name': self.public_club.url_name}))
        redirect_url = reverse('available_clubs')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)


    # Tests for user joining and applying to private and public clubs
    def test_user_applies_to_private_club(self):
        self.client.login(username=self.user.username, password='Password123')
        before_count = ClubMembership.objects.count()
        response = self.client.post(reverse('join_club', kwargs={'url_name': self.private_club.url_name}))
        after_count = ClubMembership.objects.count()
        self.assertEqual(before_count, after_count - 1)
        self.assertTrue(ClubMembership.objects.filter(user=self.user, club=self.private_club, membership=ClubMembership.UserRoles.APPLICANT).exists())
        # test appropriate message
        response_message = self.client.get(reverse('available_clubs'))
        messages_list = list(response_message.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.SUCCESS)

    def test_user_joins_public_club(self):
        self.client.login(username=self.user.username, password='Password123')
        before_count = ClubMembership.objects.count()
        response = self.client.post(self.url)
        after_count = ClubMembership.objects.count()
        self.assertEqual(before_count, after_count - 1)
        self.assertTrue(ClubMembership.objects.filter(user=self.user, club=self.public_club, membership=ClubMembership.UserRoles.MEMBER).exists())
        # test appropriate message
        response_message = self.client.get(reverse('available_clubs'))
        messages_list = list(response_message.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.SUCCESS)

    def test_user_action_invalid_club(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.post(reverse('join_club', kwargs={'url_name': "wrong"}))
        with self.assertRaises(ObjectDoesNotExist):
            Club.objects.get(url_name = "wrong").exists()
        response_message = self.client.get(reverse('available_clubs'))
        messages_list = list(response_message.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)


    def test_applicant_applies_to_private_club(self):
        self.client.login(username=self.user.username, password='Password123')
        membership = ClubMembership.objects.create(user=self.user, club=self.private_club, membership=ClubMembership.UserRoles.APPLICANT)
        membership.save()
        before_count = ClubMembership.objects.count()
        response = self.client.post(reverse('join_club', kwargs={'url_name': self.private_club.url_name}))
        after_count = ClubMembership.objects.count()
        self.assertEqual(before_count, after_count)
        self.assertTrue(ClubMembership.objects.filter(user=self.user, club=self.private_club, membership=ClubMembership.UserRoles.APPLICANT).exists())
        # test appropriate message
        response_message = self.client.get(reverse('available_clubs'))
        messages_list = list(response_message.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.INFO)

    def test_applicant_joins_public_club(self):
        self.client.login(username=self.user.username, password='Password123')
        membership = ClubMembership.objects.create(user=self.user, club=self.public_club, membership=ClubMembership.UserRoles.APPLICANT)
        membership.save()
        before_count = ClubMembership.objects.count()
        response = self.client.post(self.url)
        after_count = ClubMembership.objects.count()
        self.assertEqual(before_count, after_count)
        self.assertTrue(ClubMembership.objects.filter(user=self.user, club=self.public_club, membership=ClubMembership.UserRoles.APPLICANT).exists())
        # test appropriate message
        response_message = self.client.get(reverse('available_clubs'))
        messages_list = list(response_message.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.INFO)

    def test_applicant_action_invalid_club(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.post(reverse('join_club', kwargs={'url_name': "wrong"}))
        with self.assertRaises(ObjectDoesNotExist):
            Club.objects.get(url_name = "wrong").exists()
        response_message = self.client.get(reverse('available_clubs'))
        messages_list = list(response_message.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)


    def test_member_applies_to_private_club(self):
        self.client.login(username=self.user.username, password='Password123')
        membership = ClubMembership.objects.create(user=self.user, club=self.private_club, membership=ClubMembership.UserRoles.APPLICANT)
        membership.save()
        before_count = ClubMembership.objects.count()
        response = self.client.post(reverse('join_club', kwargs={'url_name': self.private_club.url_name}))
        after_count = ClubMembership.objects.count()
        self.assertEqual(before_count, after_count)
        self.assertTrue(ClubMembership.objects.filter(user=self.user, club=self.private_club, membership=ClubMembership.UserRoles.APPLICANT).exists())
        # test appropriate message
        response_message = self.client.get(reverse('available_clubs'))
        messages_list = list(response_message.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.INFO)

    def test_member_joins_public_club(self):
        self.client.login(username=self.user.username, password='Password123')
        membership = ClubMembership.objects.create(user=self.user, club=self.public_club, membership=ClubMembership.UserRoles.MEMBER)
        membership.save()
        before_count = ClubMembership.objects.count()
        response = self.client.post(self.url)
        after_count = ClubMembership.objects.count()
        self.assertEqual(before_count, after_count)
        self.assertTrue(ClubMembership.objects.filter(user=self.user, club=self.public_club, membership=ClubMembership.UserRoles.MEMBER).exists())
        # test appropriate message
        response_message = self.client.get(reverse('available_clubs'))
        messages_list = list(response_message.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.INFO)

    def test_member_action_invalid_club(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.post(reverse('join_club', kwargs={'url_name': "wrong"}))
        with self.assertRaises(ObjectDoesNotExist):
            Club.objects.get(url_name = "wrong").exists()
        response_message = self.client.get(reverse('available_clubs'))
        messages_list = list(response_message.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)


    def test_moderator_applies_to_private_club(self):
        self.client.login(username=self.user.username, password='Password123')
        membership = ClubMembership.objects.create(user=self.user, club=self.private_club, membership=ClubMembership.UserRoles.MODERATOR)
        membership.save()
        before_count = ClubMembership.objects.count()
        response = self.client.post(reverse('join_club', kwargs={'url_name': self.private_club.url_name}))
        after_count = ClubMembership.objects.count()
        self.assertEqual(before_count, after_count)
        self.assertTrue(ClubMembership.objects.filter(user=self.user, club=self.private_club, membership=ClubMembership.UserRoles.MODERATOR).exists())
        # test appropriate message
        response_message = self.client.get(reverse('available_clubs'))
        messages_list = list(response_message.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.INFO)

    def test_moderator_joins_public_club(self):
        self.client.login(username=self.user.username, password='Password123')
        membership = ClubMembership.objects.create(user=self.user, club=self.public_club, membership=ClubMembership.UserRoles.MODERATOR)
        membership.save()
        before_count = ClubMembership.objects.count()
        response = self.client.post(self.url)
        after_count = ClubMembership.objects.count()
        self.assertEqual(before_count, after_count)
        self.assertTrue(ClubMembership.objects.filter(user=self.user, club=self.public_club, membership=ClubMembership.UserRoles.MODERATOR).exists())
        # test appropriate message
        response_message = self.client.get(reverse('available_clubs'))
        messages_list = list(response_message.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.INFO)

    def test_moderator_action_invalid_club(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.post(reverse('join_club', kwargs={'url_name': "wrong"}))
        with self.assertRaises(ObjectDoesNotExist):
            Club.objects.get(url_name = "wrong").exists()
        response_message = self.client.get(reverse('available_clubs'))
        messages_list = list(response_message.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)


    def test_owner_applies_to_private_club(self):
        self.client.login(username=self.user.username, password='Password123')
        membership = ClubMembership.objects.create(user=self.user, club=self.private_club, membership=ClubMembership.UserRoles.OWNER)
        membership.save()
        before_count = ClubMembership.objects.count()
        response = self.client.post(reverse('join_club', kwargs={'url_name': self.private_club.url_name}))
        after_count = ClubMembership.objects.count()
        self.assertEqual(before_count, after_count)
        self.assertTrue(ClubMembership.objects.filter(user=self.user, club=self.private_club, membership=ClubMembership.UserRoles.OWNER).exists())
        # test appropriate message
        response_message = self.client.get(reverse('available_clubs'))
        messages_list = list(response_message.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.INFO)

    def test_owner_joins_public_club(self):
        self.client.login(username=self.user.username, password='Password123')
        membership = ClubMembership.objects.create(user=self.user, club=self.public_club, membership=ClubMembership.UserRoles.OWNER)
        membership.save()
        before_count = ClubMembership.objects.count()
        response = self.client.post(self.url)
        after_count = ClubMembership.objects.count()
        self.assertEqual(before_count, after_count)
        self.assertTrue(ClubMembership.objects.filter(user=self.user, club=self.public_club, membership=ClubMembership.UserRoles.OWNER).exists())
        # test appropriate message
        response_message = self.client.get(reverse('available_clubs'))
        messages_list = list(response_message.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.INFO)

    def test_owner_action_invalid_club(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.post(reverse('join_club', kwargs={'url_name': "wrong"}))
        with self.assertRaises(ObjectDoesNotExist):
            Club.objects.get(url_name = "wrong").exists()
        response_message = self.client.get(reverse('available_clubs'))
        messages_list = list(response_message.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
