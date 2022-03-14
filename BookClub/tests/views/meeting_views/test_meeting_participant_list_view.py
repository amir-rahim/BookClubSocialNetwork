"""Tests for Meeting Participants List View"""
from django.test import TestCase, tag
from django.urls import reverse

from BookClub.models import Meeting, User, Club, ClubMembership
from BookClub.tests.helpers import LogInTester


@tag('meeting', 'participants_list')
class MeetingParticipantListTestCase(TestCase, LogInTester):
    fixtures = [
        'BookClub/tests/fixtures/default_users.json',
        'BookClub/tests/fixtures/default_clubs.json',
        'BookClub/tests/fixtures/default_memberships.json',
        'BookClub/tests/fixtures/default_meetings.json',
        'BookClub/tests/fixtures/default_books.json'
    ]

    def setUp(self):
        self.organiser = User.objects.get(username='johndoe')
        self.user = User.objects.get(username='janedoe')
        self.meeting = Meeting.objects.get(pk='1')
        self.private_meeting = Meeting.objects.get(pk='4')
        self.club = Club.objects.get(pk='1')
        self.private_club = Club.objects.get(pk='3')

        self.url = reverse('meeting_participants',
                           kwargs={'club_url_name': self.club.club_url_name, 'meeting_id': self.meeting.id})

    def test_url(self):
        self.assertEqual(self.url, f'/club/{self.club.club_url_name}/meetings/{self.meeting.id}/participants/')

    def test_get_template_logged_in(self):
        self.client.login(username=self.organiser.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'meeting_participants.html')

    def test_redirect_when_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_redirect_if_not_member_of_club_private(self):
        self.client.login(username=self.organiser.username, password="Password123") 
        response = self.client.get(reverse("meeting_participants", kwargs={"club_url_name": self.private_club.club_url_name, 'meeting_id': self.private_meeting.id}))
        self.assertRedirects(response, expected_url=reverse("available_clubs"), status_code=302, target_status_code=200)

    def test_redirect_applicant(self):
        self.client.login(username=self.organiser.username, password="Password123")
        ClubMembership.objects.create(user=self.organiser, club=self.private_club,
                                      membership=ClubMembership.UserRoles.APPLICANT)
        response = self.client.get(reverse("meeting_participants",
                                           kwargs={"club_url_name": self.private_club.club_url_name,
                                                   'meeting_id': self.private_meeting.id}))
        self.assertRedirects(response, expected_url=reverse("available_clubs"), status_code=302, target_status_code=200)

    def test_non_participant_user_can_see_list(self):
        self.client.login(username='jackdoe', password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'meeting_participants.html')
        self.assertContains(response, 'johndoe')
        self.assertContains(response, 'Member')
        self.assertContains(response, 'janedoe')
        self.assertContains(response, 'Owner')

    def test_participant_user_can_see_list(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'meeting_participants.html')
        self.assertContains(response, 'johndoe')
        self.assertContains(response, 'Member')
        self.assertContains(response, 'janedoe')
        self.assertContains(response, 'Owner')

    def test_organiser_can_see_list(self):
        self.client.login(username=self.organiser.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'meeting_participants.html')
        self.assertContains(response, 'johndoe')
        self.assertContains(response, 'Member')
        self.assertContains(response, 'janedoe')
        self.assertContains(response, 'Owner')

    def test_organiser_has_admin_options(self):
        self.client.login(username=self.organiser.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "meeting_participants.html")
        self.assertContains(response, "Meeting Administration")
        self.assertContains(response, "Manage Meeting")

    def test_user_has_no_admin_options(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "meeting_participants.html")
        self.assertNotContains(response, "Meeting Administration")
        self.assertNotContains(response, "Manage Meeting")
