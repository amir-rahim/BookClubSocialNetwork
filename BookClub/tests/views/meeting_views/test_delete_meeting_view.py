"""Unit testing of the delete meeting view."""
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase, tag
from django.urls import reverse

from BookClub.models import User, Club, ClubMembership, Meeting, Book
from BookClub.tests.helpers import LogInTester


@tag('views', 'meeting', 'delete_meeting')
class DeleteMeetingView(TestCase, LogInTester):
    """Tests for the Delete Meeting view."""

    fixtures = [
        "BookClub/tests/fixtures/default_users.json",
        "BookClub/tests/fixtures/default_clubs.json",
        "BookClub/tests/fixtures/default_books.json",
        "BookClub/tests/fixtures/default_meetings.json",
    ]

    def setUp(self):
        self.organiser = User.objects.get(pk=1)
        self.owner = User.objects.get(pk=2)
        self.moderator = User.objects.get(pk=3)
        self.member = User.objects.get(pk=4)
        self.applicant = User.objects.get(pk=5)

        self.book = Book.objects.get(pk=1)
        self.meeting = Meeting.objects.get(pk=1)
        self.club = Club.objects.get(pk=1)
        self.url = reverse('delete_meeting',
                           kwargs={'club_url_name': self.club.club_url_name, 'meeting_id': self.meeting.id})

        ClubMembership.objects.create(user=self.organiser, club=self.club,
                                      membership=ClubMembership.UserRoles.MODERATOR)
        ClubMembership.objects.create(user=self.owner, club=self.club, membership=ClubMembership.UserRoles.OWNER)
        ClubMembership.objects.create(user=self.moderator, club=self.club,
                                      membership=ClubMembership.UserRoles.MODERATOR)
        ClubMembership.objects.create(user=self.member, club=self.club, membership=ClubMembership.UserRoles.MEMBER)
        ClubMembership.objects.create(user=self.applicant, club=self.club,
                                      membership=ClubMembership.UserRoles.APPLICANT)

    def test_delete_meeting_url(self):
        self.assertEqual(self.url, f'/club/{self.club.club_url_name}/meetings/{self.meeting.id}/delete/')

    def test_get_delete_meeting_redirects_to_meeting_list(self):
        """Test for redirecting user to meeting list when used get method."""

        self.client.login(username=self.owner.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url, {'user': self.owner.username})
        redirect_url = reverse('meeting_list', kwargs={'club_url_name': self.club.club_url_name})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_delete_meeting_not_logged_in_redirect(self):
        """Test for a guest unsuccessfully trying to delete a meeting"""
        self.assertFalse(self._is_logged_in())
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        self.client.post(self.url)

        meeting_exists_before = Meeting.objects.filter(pk=self.meeting.id).exists()
        self.assertEqual(meeting_exists_before, True)
        meeting_exists_after = Meeting.objects.filter(pk=self.meeting.id).exists()
        self.assertEqual(meeting_exists_before, meeting_exists_after)

    """Unit tests for user being able to delete a meeting"""

    def test_owner_can_delete_meeting(self):
        self.client.login(username=self.owner.username, password="Password123")
        self.assertTrue(self._is_logged_in())
        meeting_exists_before = Meeting.objects.filter(pk=self.meeting.id).exists()
        self.assertEqual(meeting_exists_before, True)
        response = self.client.post(self.url)
        redirect_url = reverse('meeting_list', kwargs={'club_url_name': self.club.club_url_name})
        response_message = self.client.get(redirect_url)
        messages_list = list(response_message.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.SUCCESS)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        meeting_exists_after = Meeting.objects.filter(pk=self.meeting.id).exists()
        self.assertEqual(meeting_exists_after, False)

    def test_organiser_can_delete_meeting(self):
        self.client.login(username=self.organiser.username, password="Password123")
        self.assertTrue(self._is_logged_in())
        meeting_exists_before = Meeting.objects.filter(pk=self.meeting.id).exists()
        self.assertEqual(meeting_exists_before, True)
        response = self.client.post(self.url)
        redirect_url = reverse('meeting_list', kwargs={'club_url_name': self.club.club_url_name})
        response_message = self.client.get(redirect_url)
        messages_list = list(response_message.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.SUCCESS)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        meeting_exists_after = Meeting.objects.filter(pk=self.meeting.id).exists()
        self.assertEqual(meeting_exists_after, False)

    """Unit tests for user not being able to delete a valid meeting"""

    def test_moderator_cannot_delete_meeting(self):
        self.client.login(username=self.moderator.username, password="Password123")
        self.assertTrue(self._is_logged_in())
        meeting_exists_before = Meeting.objects.filter(pk=self.meeting.id).exists()
        self.assertEqual(meeting_exists_before, True)
        response = self.client.post(self.url)
        redirect_url = reverse('meeting_list', kwargs={'club_url_name': self.club.club_url_name})
        response_message = self.client.get(redirect_url)
        messages_list = list(response_message.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        meeting_exists_after = Meeting.objects.filter(pk=self.meeting.id).exists()
        self.assertEqual(meeting_exists_before, meeting_exists_after)

    def test_member_cannot_delete_meeting(self):
        self.client.login(username=self.member.username, password="Password123")
        self.assertTrue(self._is_logged_in())
        meeting_exists_before = Meeting.objects.filter(pk=self.meeting.id).exists()
        self.assertEqual(meeting_exists_before, True)
        response = self.client.post(self.url)
        redirect_url = reverse('meeting_list', kwargs={'club_url_name': self.club.club_url_name})
        response_message = self.client.get(redirect_url)
        messages_list = list(response_message.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        meeting_exists_after = Meeting.objects.filter(pk=self.meeting.id).exists()
        self.assertEqual(meeting_exists_before, meeting_exists_after)

    def test_applicant_cannot_delete_meeting(self):
        self.client.login(username=self.applicant.username, password="Password123")
        self.assertTrue(self._is_logged_in())
        meeting_exists_before = Meeting.objects.filter(pk=self.meeting.id).exists()
        self.assertEqual(meeting_exists_before, True)
        response = self.client.post(self.url)
        redirect_url = reverse('meeting_list', kwargs={'club_url_name': self.club.club_url_name})
        response_message = self.client.get(reverse('club_dashboard', kwargs={'club_url_name': self.club.club_url_name}))
        messages_list = list(response_message.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=302)
        meeting_exists_after = Meeting.objects.filter(pk=self.meeting.id).exists()
        self.assertEqual(meeting_exists_before, meeting_exists_after)

    """Unit tests for user not being able to delete an invalid meeting"""

    def test_owner_delete_invalid_meeting(self):
        self.client.login(username=self.owner.username, password='Password123')
        response = self.client.post(reverse('delete_meeting',
                                            kwargs={'club_url_name': self.club.club_url_name,
                                                    'meeting_id': self.meeting.id + 9999}))
        redirect_url = reverse('meeting_list', kwargs={'club_url_name': self.club.club_url_name})
        with self.assertRaises(ObjectDoesNotExist):
            Meeting.objects.get(id=self.meeting.id + 9999).exists()
        response_message = self.client.get(redirect_url)
        messages_list = list(response_message.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_organiser_delete_invalid_meeting(self):
        self.client.login(username=self.organiser.username, password='Password123')
        response = self.client.post(reverse('delete_meeting',
                                            kwargs={'club_url_name': self.club.club_url_name,
                                                    'meeting_id': self.meeting.id + 9999}))
        redirect_url = reverse('meeting_list', kwargs={'club_url_name': self.club.club_url_name})
        with self.assertRaises(ObjectDoesNotExist):
            Meeting.objects.get(id=self.meeting.id + 9999).exists()
        response_message = self.client.get(redirect_url)
        messages_list = list(response_message.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_moderator_delete_invalid_meeting(self):
        self.client.login(username=self.moderator.username, password='Password123')
        response = self.client.post(reverse('delete_meeting',
                                            kwargs={'club_url_name': self.club.club_url_name,
                                                    'meeting_id': self.meeting.id + 9999}))
        redirect_url = reverse('meeting_list', kwargs={'club_url_name': self.club.club_url_name})
        with self.assertRaises(ObjectDoesNotExist):
            Meeting.objects.get(id=self.meeting.id + 9999).exists()
        response_message = self.client.get(redirect_url)
        messages_list = list(response_message.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_member_delete_invalid_meeting(self):
        self.client.login(username=self.member.username, password='Password123')
        response = self.client.post(reverse('delete_meeting',
                                            kwargs={'club_url_name': self.club.club_url_name,
                                                    'meeting_id': self.meeting.id + 9999}))
        redirect_url = reverse('meeting_list', kwargs={'club_url_name': self.club.club_url_name})
        with self.assertRaises(ObjectDoesNotExist):
            Meeting.objects.get(id=self.meeting.id + 9999).exists()
        response_message = self.client.get(redirect_url)
        messages_list = list(response_message.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_applicant_delete_invalid_meeting(self):
        self.client.login(username=self.applicant.username, password='Password123')
        response = self.client.post(reverse('delete_meeting',
                                            kwargs={'club_url_name': self.club.club_url_name,
                                                    'meeting_id': self.meeting.id + 9999}))
        redirect_url = reverse('meeting_list', kwargs={'club_url_name': self.club.club_url_name})
        with self.assertRaises(ObjectDoesNotExist):
            Meeting.objects.get(id=self.meeting.id + 9999).exists()
        response_message = self.client.get(reverse('club_dashboard', kwargs={'club_url_name': self.club.club_url_name}))
        messages_list = list(response_message.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=302)
