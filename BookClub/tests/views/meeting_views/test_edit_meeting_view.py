import copy

from django.contrib.messages import get_messages
from django.test import TestCase, tag
from django.urls import reverse

from BookClub.models import User, Meeting, Club
from BookClub.tests.helpers import LogInTester, reverse_with_next


@tag('meeting', 'edit_meeting')
class EditMeetingTestCase(TestCase, LogInTester):
    fixtures = [
        "BookClub/tests/fixtures/default_users.json",
        "BookClub/tests/fixtures/default_clubs.json",
        "BookClub/tests/fixtures/default_books.json",
        "BookClub/tests/fixtures/default_memberships.json",
        "BookClub/tests/fixtures/default_meetings.json",
    ]

    def setUp(self):
        self.meeting = Meeting.objects.get(pk=1)
        self.moderator = User.objects.get(pk=1)
        self.owner = User.objects.get(pk=2)
        self.member = User.objects.get(pk=3)
        self.club = Club.objects.get(pk=1)
        self.kwargs = {'club_url_name': self.club.club_url_name,
                       'meeting_id': self.meeting.id}
        self.url = reverse('edit_meeting', kwargs=self.kwargs)
        self.data = {
            "meeting_time": "2022-02-22T19:00+00:00",
            "location": "Franklin Wilkins Library GS04",
            "title": "Book meeting 1",
            "description": "This is a book meeting, helll yeahhhh",
            "type": "B",
            "book": 1
        }
        self.remove_member_kwargs = copy.deepcopy(self.kwargs)
        self.remove_member_kwargs['member_id'] = self.member.id
        self.remove_member_url = reverse(
            'remove_meeting_member', kwargs=self.remove_member_kwargs)

    def test_url(self):
        self.assertEqual('/club/'+self.club.club_url_name+'/meetings/'+str(self.meeting.id)+'/edit/', self.url)

    def test_remove_member_url(self):
        self.assertEqual('/club/' + self.club.club_url_name + '/meetings/' + str(self.meeting.id) + '/edit/remove_member/' + str(self.member.id), self.remove_member_url)

    def test_redirects_if_just_member_and_not_organiser_moderator_or_owner(self):
        self.client.login(username=self.member.username,
                          password='Password123')
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, reverse('meeting_list', kwargs = {'club_url_name':self.club.club_url_name}), status_code=302, target_status_code=200)

    def test_post_edit_review_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.post(self.url, self.data, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200, fetch_redirect_response=True)
        self.assertTemplateUsed(response, 'login.html')

    def test_post_remove_member_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('login', self.remove_member_url)
        response = self.client.post(self.remove_member_url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200,
                             fetch_redirect_response=True)
        self.assertTemplateUsed(response, 'login.html')

    def test_can_access_if_owner(self):
        self.client.login(username=self.owner.username,
                          password='Password123')
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url, follow=True)
        self.assertTemplateUsed(response, 'edit_meeting.html')

    def test_can_access_if_moderator(self):
        self.client.login(username=self.moderator.username,
                          password='Password123')
        response = self.client.get(self.url, follow=True)
        self.assertTemplateUsed(response, 'edit_meeting.html')

    def test_all_fields_displayed(self):
        self.client.login(username=self.owner.username,
                        password='Password123')
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url, follow=True)
        self.assertTemplateUsed(response, 'edit_meeting.html')
        self.assertContains(response, 'Title')
        self.assertContains(response, 'Description')
        self.assertContains(response, 'Meeting time')
        self.assertContains(response, 'Location')
        self.assertContains(response, 'Type')

    def test_member_displayed(self):
        self.meeting.members.add(self.member)
        self.client.login(username=self.owner.username,
                          password='Password123')
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url, follow=True)
        self.assertTemplateUsed(response, 'edit_meeting.html')
        self.assertContains(response, self.member.username)

    def test_members_displayed_but_not_owner(self):
        self.meeting.members.add(self.member)
        self.meeting.members.add(self.moderator)
        self.client.login(username=self.owner.username,
                          password='Password123')
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url, follow=True)
        self.assertTemplateUsed(response, 'edit_meeting.html')
        self.assertContains(response, self.member.username)
        self.assertContains(response, self.owner.username)
        self.assertNotContains(response, self.moderator.username)

    def test_edit_meeting_valid_data(self):
        self.client.login(username=self.owner.username,
                          password='Password123')
        self.assertTrue(self._is_logged_in())
        pre_test = self.meeting
        self.data['title'] = "ReplacedText"
        self.data['location'] = "ReplacedLocation"
        self.data['description'] = "ReplacedDescription"
        self.data['meeting_time'] = "2022-02-22T19:04+00:00"
        response = self.client.post(self.url, self.data)
        responseUrl = reverse('meeting_details', kwargs=self.kwargs)
        self.assertRedirects(response, responseUrl, status_code=302, target_status_code=200)
        post_test = Meeting.objects.get(pk=1)
        self.assertNotEqual(pre_test.title, post_test.title)
        self.assertNotEqual(pre_test.location, post_test.location)
        self.assertNotEqual(pre_test.description, post_test.description)
        self.assertNotEqual(pre_test.meeting_time, post_test.meeting_time)

    def test_edit_invalid_meeting(self):
        self.client.login(username=self.owner.username,
                          password='Password123')
        self.assertTrue(self._is_logged_in())
        self.url = reverse('edit_meeting', kwargs={'meeting_id': self.meeting.id+9999, 'club_url_name': self.club.club_url_name})
        response = self.client.post(self.url, self.data, follow=True)
        redirect_url = reverse('meeting_list', kwargs={'club_url_name': self.club.club_url_name})
        messages_list = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 2)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200,
                             fetch_redirect_response=True)
        self.assertTemplateUsed(response, 'club_meetings.html')

    def test_edit_meeting_post_invalid_data(self):
        self.client.login(username=self.owner.username,
                          password='Password123')
        self.assertTrue(self._is_logged_in())
        pre_test = self.meeting
        self.data['title'] = ""
        self.data['location'] = ""
        self.data['description'] = ""
        self.data['meeting_time'] = "some random time"
        response = self.client.post(self.url, self.data)
        self.assertTemplateUsed(response, 'edit_meeting.html')
        post_test = Meeting.objects.get(pk=1)
        self.assertEqual(pre_test.title, post_test.title)
        self.assertEqual(pre_test.location, post_test.location)
        self.assertEqual(pre_test.description, post_test.description)
        self.assertEqual(pre_test.meeting_time, post_test.meeting_time)

    def test_remove_member_owner_organiser(self):
        self.meeting.members.add(self.member)
        self.client.login(username=self.owner.username, password="Password123")
        self.assertTrue(self._is_logged_in())
        pre_test_response = self.client.get(self.url)
        self.assertContains(pre_test_response, self.member.username)
        pre_test = self.meeting
        response = self.client.post(self.remove_member_url, follow=True)
        self.assertTemplateUsed(response, 'edit_meeting.html')
        post_test = Meeting.objects.get(pk=1)
        self.assertNotEqual(pre_test.members.all(), post_test.members.all())
        post_test_response = self.client.get(self.url)
        self.assertNotContains(post_test_response, self.member.username)

    def test_remove_member_remove_organiser(self):
        self.client.login(username=self.owner.username, password="Password123")
        self.assertTrue(self._is_logged_in())
        pre_test = self.meeting
        self.remove_member_kwargs['member_id'] = self.moderator.id
        self.remove_member_url = reverse('remove_meeting_member', kwargs=self.remove_member_kwargs)
        response = self.client.post(self.remove_member_url, follow=True)
        self.assertTemplateUsed(response, 'edit_meeting.html')
        post_test = Meeting.objects.get(pk=1)
        self.assertEqual(pre_test.members.all().count(), post_test.members.all().count())

    def test_remove_member_moderator(self):
        self.meeting.members.add(self.member)
        self.client.login(username=self.moderator.username, password="Password123")
        self.assertTrue(self._is_logged_in())
        pre_test_response = self.client.get(self.url)
        self.assertContains(pre_test_response, self.member.username)
        pre_test = Meeting.objects.get(pk=1)
        response = self.client.post(self.remove_member_url, follow=True)
        self.assertTemplateUsed(response, 'edit_meeting.html')
        post_test = Meeting.objects.get(pk=1)
        self.assertNotEqual(pre_test.members.all(), post_test.members.all())
        post_test_response = self.client.get(self.url)
        self.assertNotContains(post_test_response, self.member.username)

    def test_remove_member_fails_as_non_owner_or_moderator_or_organiser(self):
        self.client.login(username=self.member.username,
                          password="Password123")
        self.assertTrue(self._is_logged_in())
        pre_test = self.meeting
        response = self.client.post(self.remove_member_url, follow=True)
        self.assertRedirects(response, reverse('meeting_list', kwargs={'club_url_name': self.club.club_url_name}),
                             status_code=302, target_status_code=200)
        post_test = Meeting.objects.get(pk=1)
        self.assertEqual(pre_test.members.all().count(), post_test.members.all().count())

    def test_remove_invalid_member(self):
        self.client.login(username=self.owner.username,
                          password='Password123')
        self.assertTrue(self._is_logged_in())
        self.remove_member_kwargs['meeting_id'] = self.meeting.id+9999
        self.remove_member_url = reverse('remove_meeting_member', kwargs=self.remove_member_kwargs)
        response = self.client.post(self.remove_member_url, follow=True)
        messages_list = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertTemplateUsed(response, 'club_meetings.html')
