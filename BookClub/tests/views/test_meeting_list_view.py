from BookClub.models import User, Club, ClubMembership,Meeting
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase, tag
from django.urls import reverse


@tag('meetinglist')
class MeetingListTest(TestCase):
    
    fixtures = [
        'BookClub/tests/fixtures/default_users.json',
        'BookClub/tests/fixtures/default_clubs.json',
        'BookClub/tests/fixtures/default_meetings.json',
        'BookCLub/tests/fixtures/default_books.json'
    ]

    def setUp(self):
        self.club = Club.objects.get(pk=1)
        self.meeting = Meeting.objects.get(pk=1,club=self.club)
        self.meeting2 = Meeting.objects.get(pk=2,club=self.club)
        self.url = reverse("meeting_list",kwargs={'club_url_name':self.club.club_url_name})
        self.john = User.objects.get(username="johndoe")
        self.jane = User.objects.get(username="janedoe")
        self.jack = User.objects.get(username="jackdoe")
        

    def test_url(self):
        url = f'/club/{self.club.club_url_name}/meetings/'
        self.assertEqual(self.url,url)

    def test_get_template_logged_in(self):
        self.client.login(username=self.john.username, password="Password123")
        response = self.client.get(self.url) #error here
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_meetings.html')

    def test_redirect_when_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_can_see_club_name(self):
        self.client.login(username=self.john.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_meetings.html')
        self.assertContains(response, self.club.name)

    def test_can_see_club_name(self):
        self.client.login(username=self.john.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_meetings.html')
        self.assertContains(response, self.club.name)

    def test_can_see_a_meeting(self):
        self.client.login(username = self.john.username, password = "Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_meetings.html')
        self.assertContains(response,'Book meeting 1')
        # self.assertContains(response,'2022-02-22T19:00+00:00')
        self.assertContains(response,'johndoe')

    def test_can_see_multiple_meetings(self):
        self.client.login(username = self.john.username, password = "Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_meetings.html')

        self.assertContains(response,'Book meeting 1')
        self.assertContains(response,'johndoe')

        self.assertContains(response,'Book meeting 2')
        self.assertContains(response,'janedoe')

    #Need to add tests involving the action views ()
    #test contains correct info
    #test multiple meetings
    

