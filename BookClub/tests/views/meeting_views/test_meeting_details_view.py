"""Tests for Meeting Details View"""
from django.test import TestCase, tag
from django.urls import reverse

from BookClub.models import Meeting, User, Club
from BookClub.models.club_membership import ClubMembership
from BookClub.tests.helpers import LogInTester


@tag('meeting', 'meeting_details')
class MeetingDetailsViewTestCase(TestCase, LogInTester):
    """Tests for Meeting Details View"""

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

        self.url = reverse('meeting_details',
                           kwargs={'club_url_name': self.club.club_url_name, 'meeting_id': self.meeting.id})

    def test_url(self):
        self.assertEqual(self.url, '/club/' + self.club.club_url_name + '/meetings/' + str(self.meeting.id) + '/')

    def test_redirects_when_not_logged_in(self):
        self.assertFalse(self._is_logged_in())
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_redirect_if_not_member_of_club_private(self):
        # johndoe is not in the private club
        self.client.login(username=self.organiser.username, password="Password123")
        response = self.client.get(reverse("meeting_details", kwargs={"club_url_name": self.private_club.club_url_name,
                                                                      'meeting_id': self.private_meeting.id}))
        self.assertRedirects(response, expected_url=reverse("available_clubs"), status_code=302, target_status_code=200)

    def test_redirect_applicant(self):
        self.client.login(username=self.organiser.username, password="Password123")
        ClubMembership.objects.create(user=self.organiser, club=self.private_club,
                                      membership=ClubMembership.UserRoles.APPLICANT)
        response = self.client.get(reverse("meeting_details", kwargs={"club_url_name": self.private_club.club_url_name,
                                                                      'meeting_id': self.private_meeting.id}))
        self.assertRedirects(response, expected_url=reverse("available_clubs"), status_code=302, target_status_code=200)

    def test_user_can_see_meeting_name_and_club(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "meeting_details.html")
        self.assertContains(response, "Book meeting 1")
        self.assertContains(response, "Johnathan Club")

    def test_organiser_can_see_meeting_details_book_meeting(self):
        self.client.login(username=self.organiser.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "meeting_details.html")
        self.assertContains(response, "Feb. 22, 2022, 7 p.m.")
        self.assertContains(response, "Feb. 10, 2022")
        self.assertContains(response, "Franklin Wilkins Library GS04")
        self.assertContains(response, "Book meeting 1")
        self.assertContains(response, "This is a book meeting, helll yeahhhh")
        self.assertContains(response, "2")
        self.assertContains(response, "Book")
        self.assertContains(response, "Classical Mythology")

    def test_user_can_see_meeting_details_book_meeting(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "meeting_details.html")
        self.assertContains(response, "Feb. 22, 2022, 7 p.m.")
        self.assertContains(response, "Feb. 10, 2022")
        self.assertContains(response, "Franklin Wilkins Library GS04")
        self.assertContains(response, "Book meeting 1")
        self.assertContains(response, "This is a book meeting, helll yeahhhh")
        self.assertContains(response, "2")
        self.assertContains(response, "Book")
        self.assertContains(response, "Classical Mythology")

    def test_organiser_can_see_details_social_meeting(self):
        self.client.login(username=self.organiser.username, password="Password123")
        social_meeting = Meeting.objects.get(pk='5')
        social_meeting_url = reverse('meeting_details',
                                     kwargs={'club_url_name': self.club.club_url_name, 'meeting_id': social_meeting.id})
        response = self.client.get(social_meeting_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "meeting_details.html")
        self.assertContains(response, "Feb. 22, 2022, 7 p.m.")
        self.assertContains(response, "Feb. 10, 2022")
        self.assertContains(response, "Franklin Wilkins Library GS04")
        self.assertContains(response, "Social meeting 1")
        self.assertContains(response, "This is a social meeting, helll yeahhhh")
        self.assertContains(response, "2")
        self.assertContains(response, "Social")

    def test_user_can_see_details_social_meeting(self):
        self.client.login(username=self.user.username, password="Password123")
        social_meeting = Meeting.objects.get(pk='5')
        social_meeting_url = reverse('meeting_details',
                                     kwargs={'club_url_name': self.club.club_url_name, 'meeting_id': social_meeting.id})
        response = self.client.get(social_meeting_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "meeting_details.html")
        self.assertContains(response, "Feb. 22, 2022, 7 p.m.")
        self.assertContains(response, "Feb. 10, 2022")
        self.assertContains(response, "Franklin Wilkins Library GS04")
        self.assertContains(response, "Social meeting 1")
        self.assertContains(response, "This is a social meeting, helll yeahhhh")
        self.assertContains(response, "2")
        self.assertContains(response, "Social")

    def test_organiser_can_see_details_club_meeting(self):
        self.client.login(username=self.organiser.username, password="Password123")
        club_meeting = Meeting.objects.get(pk='6')
        club_meeting_url = reverse('meeting_details',
                                   kwargs={'club_url_name': self.club.club_url_name, 'meeting_id': club_meeting.id})
        response = self.client.get(club_meeting_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "meeting_details.html")
        self.assertContains(response, "Feb. 22, 2022, 7 p.m.")
        self.assertContains(response, "Feb. 10, 2022")
        self.assertContains(response, "Franklin Wilkins Library GS04")
        self.assertContains(response, "Club meeting 1")
        self.assertContains(response, "This is a club meeting, helll yeahhhh")
        self.assertContains(response, "2")
        self.assertContains(response, "Club")

    def test_user_can_see_details_club_meeting(self):
        self.client.login(username=self.user.username, password="Password123")
        club_meeting = Meeting.objects.get(pk='6')
        club_meeting_url = reverse('meeting_details',
                                   kwargs={'club_url_name': self.club.club_url_name, 'meeting_id': club_meeting.id})
        response = self.client.get(club_meeting_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "meeting_details.html")
        self.assertContains(response, "Feb. 22, 2022, 7 p.m.")
        self.assertContains(response, "Feb. 10, 2022")
        self.assertContains(response, "Franklin Wilkins Library GS04")
        self.assertContains(response, "Club meeting 1")
        self.assertContains(response, "This is a club meeting, helll yeahhhh")
        self.assertContains(response, "2")
        self.assertContains(response, "Club")

    def test_organiser_can_see_details_other_meeting(self):
        self.client.login(username=self.organiser.username, password="Password123")
        other_meeting = Meeting.objects.get(pk='7')
        other_meeting_url = reverse('meeting_details',
                                    kwargs={'club_url_name': self.club.club_url_name, 'meeting_id': other_meeting.id})
        response = self.client.get(other_meeting_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "meeting_details.html")
        self.assertContains(response, "Feb. 22, 2022, 7 p.m.")
        self.assertContains(response, "Feb. 10, 2022")
        self.assertContains(response, "Franklin Wilkins Library GS04")
        self.assertContains(response, "Other meeting 1")
        self.assertContains(response, "This is an other meeting, helll yeahhhh")
        self.assertContains(response, "2")
        self.assertContains(response, "Other")

    def test_user_can_see_details_other_meeting(self):
        self.client.login(username=self.user.username, password="Password123")
        other_meeting = Meeting.objects.get(pk='7')
        other_meeting_url = reverse('meeting_details',
                                    kwargs={'club_url_name': self.club.club_url_name, 'meeting_id': other_meeting.id})
        response = self.client.get(other_meeting_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "meeting_details.html")
        self.assertContains(response, "Feb. 22, 2022, 7 p.m.")
        self.assertContains(response, "Feb. 10, 2022")
        self.assertContains(response, "Franklin Wilkins Library GS04")
        self.assertContains(response, "Other meeting 1")
        self.assertContains(response, "This is an other meeting, helll yeahhhh")
        self.assertContains(response, "2")
        self.assertContains(response, "Other")

    def test_organiser_can_see_organiser_info(self):
        self.client.login(username=self.organiser.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "meeting_details.html")
        self.assertContains(response, "johndoe")
        self.assertContains(response, "johndoe@example.com")

    def test_user_can_see_organiser_info(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "meeting_details.html")
        self.assertContains(response, "johndoe")
        self.assertContains(response, "johndoe@example.com")

    def test_organiser_has_admin_options(self):
        self.client.login(username=self.organiser.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "meeting_details.html")
        self.assertContains(response, "Manage Meeting")

    def test_user_has_no_admin_options(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "meeting_details.html")
        self.assertNotContains(response, "Manage Meeting")

    def test_invalid_club(self):
        self.client.login(username=self.organiser.username, password="Password123")
        response = self.client.get(
            reverse("meeting_details", kwargs={"club_url_name": 'fakeclub', "meeting_id": '100'}))
        self.assertRedirects(response, expected_url=reverse("available_clubs"), status_code=302, target_status_code=200)
