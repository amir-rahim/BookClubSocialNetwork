from django.test import TestCase, tag
from django.urls import reverse
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from BookClub.tests.helpers import LogInTester
from BookClub.models import User, Meeting, Club, ClubMembership
from django.utils import timezone

@tag("meeting","leavemeetingview")
class LeaveMeetingViewTestCase(TestCase, LogInTester):
    """Tests of the Join Meeting view."""

    fixtures = [
        'BookClub/tests/fixtures/default_users.json',
        'BookClub/tests/fixtures/default_clubs.json',
        'BookClub/tests/fixtures/default_meetings.json',
        'BookClub/tests/fixtures/books.json',
    ]

    def setUp(self):
        self.user = User.objects.get(username="johndoe")
        self.organiser = User.objects.get(username="janedoe")
        self.club = Club.objects.get(pk="1")
        self.past_meeting = Meeting.objects.get(pk = "2")
        self.future_meeting = Meeting.objects.get(pk = "3")

        self.url = reverse('leave_meeting', kwargs={'club_url_name' : self.club.club_url_name, 'meeting_id': self.future_meeting.id})

    def test_url(self):
        self.assertEqual(self.url,f'/club/{self.club.club_url_name}/meetings/{self.future_meeting.id}/leave')

    def test_redirect_when_not_logged_in(self):
        self.assertFalse(self._is_logged_in())
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_get_leave_meeting_redirects_to_list_of_meetings(self):
        """Test for redirecting user to available_clubs when used get method."""

        self.client.login(username=self.user.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        response = self.client.get(reverse('leave_meeting', kwargs={'club_url_name' : self.club.club_url_name, 'meeting_id': self.future_meeting.id}))
        redirect_url = reverse('home') # should be meeting list
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_member_successful_leave_meeting(self):
        self.client.login(username=self.user.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        ClubMembership.objects.create(user=self.user, club=self.club, membership=ClubMembership.UserRoles.MEMBER)
        self.future_meeting.join_member(self.user)
        before_count = self.future_meeting.get_members().count()
        response = self.client.post(reverse('leave_meeting', kwargs={
                                                                'club_url_name': self.club.club_url_name, 
                                                                'meeting_id' : self.future_meeting.id
                                                            }))     
        after_count = self.future_meeting.get_members().count()
        self.assertEqual(before_count, after_count + 1)                                                     
        self.assertFalse(self.future_meeting.get_members().filter(username = self.user.username).exists())
        response_message = self.client.get(reverse('leave_meeting', kwargs={'club_url_name' : self.club.club_url_name, 'meeting_id': self.future_meeting.id}))
        messages_list = list(response_message.context['messages']) 
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.SUCCESS)

    def test_member_leave_meeting_not_in(self):
        self.client.login(username=self.user.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        ClubMembership.objects.create(user=self.user, club=self.club, membership=ClubMembership.UserRoles.MEMBER)
        self.assertFalse(self.future_meeting.get_members().filter(username = self.user.username).exists())
        before_count = self.future_meeting.get_members().count()
        response = self.client.post(reverse('leave_meeting', kwargs={
                                                                'club_url_name': self.club.club_url_name, 
                                                                'meeting_id' : self.future_meeting.id
                                                            }))     
        after_count = self.future_meeting.get_members().count()
        self.assertEqual(before_count, after_count)                                                       
        self.assertFalse(self.future_meeting.get_members().filter(username = self.user.username).exists())
        response_message = self.client.get(reverse('leave_meeting', kwargs={'club_url_name' : self.club.club_url_name, 'meeting_id': self.future_meeting.id}))
        messages_list = list(response_message.context['messages']) 
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.INFO)

    def test_member_cannot_leave_meeting_in_past(self):
        self.client.login(username=self.user.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        ClubMembership.objects.create(user=self.user, club=self.club, membership=ClubMembership.UserRoles.MEMBER)
        self.assertTrue(self.past_meeting.get_meeting_time() < timezone.now())
        before_count = self.past_meeting.get_members().count()
        response = self.client.post(reverse('leave_meeting', kwargs={
                                                                'club_url_name': self.club.club_url_name, 
                                                                'meeting_id' : self.past_meeting.id
                                                            }))     
        after_count = self.past_meeting.get_members().count()
        self.assertEqual(before_count, after_count)                                                     
        self.assertTrue(self.past_meeting.get_members().filter(username = self.user.username).exists())
        response_message = self.client.get(reverse('leave_meeting', kwargs={'club_url_name' : self.club.club_url_name, 'meeting_id': self.past_meeting.id}))
        messages_list = list(response_message.context['messages']) 
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.INFO)
    
    def test_member_cannot_leave_invalid_meeting(self):
        self.client.login(username=self.user.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        ClubMembership.objects.create(user=self.user, club=self.club, membership=ClubMembership.UserRoles.MEMBER)
        response = self.client.post(reverse('leave_meeting', kwargs={
                                                                'club_url_name': self.club.club_url_name, 
                                                                'meeting_id' : 0
                                                            })) 
        with self.assertRaises(ObjectDoesNotExist):
            Meeting.objects.get(id = 0).exists()     
        response_message = self.client.get(reverse('leave_meeting', kwargs={'club_url_name': self.club.club_url_name, 'meeting_id' : 0}))
        messages_list = list(response_message.context['messages']) 
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

    def test_organiser_cannot_leave_meeting(self):
        self.client.login(username=self.organiser.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        ClubMembership.objects.create(user=self.user, club=self.club, membership=ClubMembership.UserRoles.MODERATOR)
        self.future_meeting.join_member(self.user)
        before_count = self.future_meeting.get_members().count()
        response = self.client.post(reverse('join_meeting', kwargs={
                                                                'club_url_name': self.club.club_url_name, 
                                                                'meeting_id' : self.future_meeting.id
                                                            }))     
        after_count = self.future_meeting.get_members().count()
        self.assertEqual(before_count, after_count)                                                         
        self.assertTrue(self.future_meeting.get_members().filter(username = self.organiser.username).exists())
        response_message = self.client.get(reverse('join_meeting', kwargs={'club_url_name' : self.club.club_url_name, 'meeting_id': self.future_meeting.id}))
        messages_list = list(response_message.context['messages']) 
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.INFO)