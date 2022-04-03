"""Unit testing of the Create Meeting view."""
from django.contrib import messages
from django.contrib.messages import get_messages
from django.test import TestCase, tag
from django.urls import reverse

from BookClub.forms.meeting import MeetingForm
from BookClub.models import User, Club, ClubMembership, Meeting, Book
from BookClub.tests.helpers import reverse_with_next


@tag('views', 'meeting', 'create_meeting')
class CreateMeetingViewTestCase(TestCase):
    """Tests for the Create Meeting view."""

    fixtures = [
        "BookClub/tests/fixtures/default_users.json",
        "BookClub/tests/fixtures/default_clubs.json",
        "BookClub/tests/fixtures/default_books.json",
    ]

    def setUp(self):
        self.owner = User.objects.get(pk=1)
        self.moderator = User.objects.get(pk=2)
        self.member = User.objects.get(pk=3)
        self.applicant = User.objects.get(pk=4)

        self.book = Book.objects.get(pk=1)
        self.club = Club.objects.get(pk=2)
        self.private_club = Club.objects.get(pk=3)
        self.url = reverse('create_meeting', kwargs={'club_url_name': self.club.club_url_name})
        self.url_private_club = reverse('create_meeting', kwargs={'club_url_name': self.private_club.club_url_name})

        ClubMembership.objects.create(user=self.owner, club=self.club, membership=ClubMembership.UserRoles.OWNER)
        ClubMembership.objects.create(user=self.moderator, club=self.club, membership=ClubMembership.UserRoles.MODERATOR)
        ClubMembership.objects.create(user=self.member, club=self.club, membership=ClubMembership.UserRoles.MEMBER)
        ClubMembership.objects.create(user=self.applicant, club=self.club, membership=ClubMembership.UserRoles.APPLICANT)
        ClubMembership.objects.create(user=self.applicant, club=self.private_club, membership=ClubMembership.UserRoles.OWNER)

        self.data = {
            "title": "Weekly book review",
            "description": "This is our first weekly meeting for this weeks book!",
            "meeting_time": "2022-02-26 15:30:00",
            "meeting_end_time": "2022-02-26 16:30:00",
            "location": "Maughan Library",
            "type": "B",
            "book": self.book.id,
        }

    def test_create_meeting_url(self):
        self.assertEqual(self.url, f'/club/{self.club.club_url_name}/meetings/create/')

    def test_post_create_meeting_redirects_when_not_logged_in(self):
        meeting_count_before = Meeting.objects.count()
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.post(self.url, self.data, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200, fetch_redirect_response=True)
        self.assertTemplateUsed(response, 'authentication/login.html')
        meeting_count_after = Meeting.objects.count()
        self.assertEqual(meeting_count_after, meeting_count_before)

    def test_get_create_meeting_redirects_when_not_logged_in(self):
        meeting_count_before = Meeting.objects.count()
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200, fetch_redirect_response=True)
        self.assertTemplateUsed(response, 'authentication/login.html')
        meeting_count_after = Meeting.objects.count()
        self.assertEqual(meeting_count_after, meeting_count_before)

    '''Tests for users which can see the create meeting form'''

    def test_owner_can_see_create_meeting_template(self):
        self.client.login(username=self.owner.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'meeting/create_meeting.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, MeetingForm))
        self.assertFalse(form.is_bound)

    def test_moderator_can_see_create_meeting_template(self):
        self.client.login(username=self.moderator.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'meeting/create_meeting.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, MeetingForm))
        self.assertFalse(form.is_bound)

    '''Tests for users which cannot see the create meeting form'''

    def test_member_cannot_see_create_meeting_template(self):
        self.client.login(username=self.member.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        response_message = self.client.get(reverse('club_dashboard', kwargs={'club_url_name': self.club.club_url_name}))
        messages_list = list(response_message.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

    def test_applicant_cannot_see_create_meeting_template(self):
        self.client.login(username=self.applicant.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        response_message = self.client.get(reverse('club_dashboard', kwargs={'club_url_name': self.club.club_url_name}))
        messages_list = list(response_message.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

    '''Tests for users successfully creating a meeting'''

    def test_owner_create_meeting(self):
        self.client.login(username=self.owner.username, password='Password123')
        before_count = Meeting.objects.count()
        response = self.client.post(self.url, self.data, follow=True)
        meeting = Meeting.objects.get(title=self.data['title'])
        messages_list = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.SUCCESS)
        after_count = Meeting.objects.count()
        self.assertEqual(after_count, before_count + 1)
        self.assertTemplateUsed(response, 'meeting/club_meetings.html')
        self.assertEqual(meeting.title, self.data['title'])
        self.assertEqual(meeting.description, self.data['description'])
        self.assertEqual(meeting.location, self.data['location'])
        self.assertEqual(meeting.type, self.data['type'])
        self.assertEqual(meeting.book.id, self.data['book'])

    def test_moderator_create_meeting(self):
        self.client.login(username=self.moderator.username, password='Password123')
        before_count = Meeting.objects.count()
        response = self.client.post(self.url, self.data, follow=True)
        meeting = Meeting.objects.get(title=self.data['title'])
        messages_list = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.SUCCESS)
        after_count = Meeting.objects.count()
        self.assertEqual(after_count, before_count + 1)
        self.assertTemplateUsed(response, 'meeting/club_meetings.html')
        self.assertEqual(meeting.title, self.data['title'])
        self.assertEqual(meeting.description, self.data['description'])
        self.assertEqual(meeting.location, self.data['location'])
        self.assertEqual(meeting.type, self.data['type'])
        self.assertEqual(meeting.book.id, self.data['book'])

    '''Tests for users with permission unsuccessfully creating a meeting'''

    def test_owner_create_wrong_meeting(self):
        self.client.login(username=self.owner.username, password='Password123')
        self.data['meeting_time'] = "2022-02-26 17:30:00"
        before_count = Meeting.objects.count()
        response = self.client.post(self.url, self.data)
        after_count = Meeting.objects.count()
        self.assertEqual(after_count, before_count)
        messages_list = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'meeting/create_meeting.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, MeetingForm))
        self.assertTrue(form.is_bound)

    def test_moderator_create_wrong_meeting(self):
        self.client.login(username=self.moderator.username, password='Password123')
        self.data['meeting_time'] = "2022-02-26 17:30:00"
        before_count = Meeting.objects.count()
        response = self.client.post(self.url, self.data)
        after_count = Meeting.objects.count()
        self.assertEqual(after_count, before_count)
        messages_list = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'meeting/create_meeting.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, MeetingForm))
        self.assertTrue(form.is_bound)

    def test_moderator_create_meeting_with_incorrect_end_time(self):
        self.client.login(username=self.moderator.username, password='Password123')
        self.data['meeting_end_time'] = "2022-02-26 14:30:00"
        before_count = Meeting.objects.count()
        response = self.client.post(self.url, self.data)
        after_count = Meeting.objects.count()
        self.assertEqual(after_count, before_count)
        messages_list = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'meeting/create_meeting.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, MeetingForm))
        self.assertTrue(form.is_bound)

    '''Tests for users not being able to creating a meeting'''

    def test_member_create_meeting(self):
        self.client.login(username=self.member.username, password='Password123')
        before_count = Meeting.objects.count()
        response = self.client.post(self.url, self.data, follow=True)
        messages_list = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        after_count = Meeting.objects.count()
        self.assertEqual(after_count, before_count)

    def test_applicant_create_meeting(self):
        self.client.login(username=self.applicant.username, password='Password123')
        before_count = Meeting.objects.count()
        response = self.client.post(self.url, self.data, follow=True)
        messages_list = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        after_count = Meeting.objects.count()
        self.assertEqual(after_count, before_count)

    '''Tests for users creating meetings for another club'''

    def test_owner_of_club_cannot_create_meetings_for_another_private_club(self):
        self.client.login(username=self.owner.username, password='Password123')
        response = self.client.post(self.url_private_club, self.data, follow=True)
        self.assertEqual(response.status_code, 200)
        response_message = self.client.get(reverse('available_clubs'))
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        self.assertTemplateUsed(response, 'clubs/available_clubs.html')

    def test_moderator_of_club_cannot_create_meetings_for_another_private_club(self):
        self.client.login(username=self.moderator.username, password='Password123')
        response = self.client.post(self.url_private_club, self.data, follow=True)
        self.assertEqual(response.status_code, 200)
        response_message = self.client.get(reverse('available_clubs'))
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        self.assertTemplateUsed(response, 'clubs/available_clubs.html')

    def test_member_of_club_cannot_create_meetings_for_another_private_club(self):
        self.client.login(username=self.member.username, password='Password123')
        response = self.client.post(self.url_private_club, self.data, follow=True)
        self.assertEqual(response.status_code, 200)
        response_message = self.client.get(reverse('available_clubs'))
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        self.assertTemplateUsed(response, 'clubs/available_clubs.html')

    '''Tests for users creating meetings for invalid club'''

    def test_owner_cannot_create_meeting_for_invalid_club(self):
        self.client.login(username=self.owner.username, password='Password123')
        before_count = Meeting.objects.count()
        response = self.client.post(reverse('create_meeting', kwargs={'club_url_name': 'wrong'}), self.data, follow=True)
        messages_list = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        after_count = Meeting.objects.count()
        self.assertEqual(after_count, before_count)

    def test_moderator_cannot_create_meeting_for_invalid_club(self):
        self.client.login(username=self.moderator.username, password='Password123')
        before_count = Meeting.objects.count()
        response = self.client.post(reverse('create_meeting', kwargs={'club_url_name': 'wrong'}), self.data, follow=True)
        messages_list = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        after_count = Meeting.objects.count()
        self.assertEqual(after_count, before_count)

    def test_member_cannot_create_meeting_for_invalid_club(self):
        self.client.login(username=self.member.username, password='Password123')
        before_count = Meeting.objects.count()
        response = self.client.post(reverse('create_meeting', kwargs={'club_url_name': 'wrong'}), self.data, follow=True)
        messages_list = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        after_count = Meeting.objects.count()
        self.assertEqual(after_count, before_count)

    def test_applicant_cannot_create_meeting_for_invalid_club(self):
        self.client.login(username=self.applicant.username, password='Password123')
        before_count = Meeting.objects.count()
        response = self.client.post(reverse('create_meeting', kwargs={'club_url_name': 'wrong'}), self.data, follow=True)
        messages_list = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        after_count = Meeting.objects.count()
        self.assertEqual(after_count, before_count)
