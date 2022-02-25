from datetime import date, datetime
from django.contrib import messages
from django.shortcuts import redirect
from django.test import TestCase, tag
from django.urls import reverse
from BookClub.models import *
from django.contrib.messages import get_messages

from BookClub.tests.helpers import reverse_with_next
@tag('editmeeting','meeting')
class EditMeetingTestCase(TestCase):
    """
    Testing for edit_meeting
    Carried out by Raymond
    """

    fixtures = [
        "BookClub/tests/fixtures/default_users.json",
        "BookClub/tests/fixtures/default_clubs.json",
        "BookClub/tests/fixtures/default_books.json",
        "BookClub/tests/fixtures/default_meetings.json",
        
    ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.meeting = Meeting.objects.get(pk=1)
        
        self.owner = User.objects.get(pk=7)
        self.applicant = User.objects.get(pk=6)
        self.member = User.objects.get(pk=5)
        self.moderator = User.objects.get(pk=4)
        self.not_in_club_user = User.objects.get(pk=3)

        self.organiser = self.meeting.organiser
        self.club = self.meeting.club

        ClubMembership.objects.create(user = self.owner, club = self.club, membership = ClubMembership.UserRoles.OWNER)
        ClubMembership.objects.create(user = self.applicant, club = self.club, membership = ClubMembership.UserRoles.APPLICANT)
        ClubMembership.objects.create(user = self.member, club = self.club, membership = ClubMembership.UserRoles.MEMBER)
        ClubMembership.objects.create(user = self.organiser,club=self.club,membership = ClubMembership.UserRoles.MODERATOR)
        ClubMembership.objects.create(user = self.moderator,club=self.club,membership = ClubMembership.UserRoles.MODERATOR)
        
        self.book = Book.objects.get(pk=1)
        self.book2 = Book.objects.get(pk=2)
        
        self.url = reverse('edit_meeting', kwargs = {'club_url_name': self.club.club_url_name,'meeting_id':self.meeting.id})
        self.title = "new title"
        self.description = "this is the new description"
        self.location = "somewhere"
        self.meetingtime = datetime.now()
        self.created = datetime(2022,2,22,15)
        self.type = Meeting.MeetingType.OTHER
        self.data = {
            'title': self.title,
            'description': self.description,
            'location': self.location,
            'meeting_time': self.meetingtime,
            'type': self.type,
            'book': self.book
        }
        #Date time input format: "yyyy-mm-dd hh:mm:ss"
    def test_edit_meeting_url(self):
        self.assertEqual(self.url,f'/club/{self.club.club_url_name}/meetings/{self.meeting.id}/edit/')

    def test_redirect_when_not_logged_in(self):
        redirect_url = reverse_with_next('login',self.url)
        response = self.client.post(self.url,self.data,follow=True)
        self.assertRedirects(response,redirect_url,status_code=302,target_status_code=200,fetch_redirect_response=True)
        self.assertTemplateUsed(response,'login.html')

    def test_redirect_when_edit_invalid_meeting(self):
        url = reverse('edit_meeting', kwargs = {'club_url_name': self.club.club_url_name,'meeting_id':100})
        redirect_url = reverse_with_next('login',url)
        response = self.client.post(url,self.data,follow=True)
        self.assertRedirects(response,redirect_url,status_code=302,target_status_code=200,fetch_redirect_response=True)
        self.assertTemplateUsed(response,'login.html')


    def test_applicant_cannot_edit_meeting(self):
        self.client.login(username=self.applicant.username,password="Password123")
        response = self.client.get(self.url)
        messages_list = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list),1)
        self.assertEqual(messages_list[0].level,messages.ERROR)
        self.assertEqual(str(messages_list[0]),"You are not allowed to do that")
        self.assertEqual(response.status_code,302)

    def test_member_cannot_edit_meeting(self):
        self.client.login(username=self.member.username,password="Password123")
        response = self.client.get(self.url)
        messages_list = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list),1)
        self.assertEqual(messages_list[0].level,messages.ERROR)
        self.assertEqual(str(messages_list[0]),"You are not allowed to do that")
        self.assertEqual(response.status_code,302)

    def test_moderator_cannot_edit_meeting(self):
        self.client.login(username=self.moderator.username,password="Password123")
        response = self.client.get(self.url)
        messages_list = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list),1)
        self.assertEqual(messages_list[0].level,messages.ERROR)
        self.assertEqual(str(messages_list[0]),"You are not allowed to do that")
        self.assertEqual(response.status_code,302)

    def test_user_not_in_club_cannot_edit_meeting(self):
        self.client.login(username=self.not_in_club_user.username,password="Password123")
        response = self.client.get(self.url)
        messages_list = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list),2)
        self.assertEqual(messages_list[0].level,messages.ERROR)
        self.assertEqual(response.status_code,302)    
        
    def test_owner_edit_meeting(self):
        self.client.login(username=self.owner.username,password="Password123")
        response = self.client.get(self.url)
        messages_list = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list),1)
        self.assertEqual(messages_list[0].level,messages.SUCCESS)
        self.assertTemplateUsed(response,'edit_meeting.html')
        
        
    def test_organiser_edit_meeting(self):
        self.client.login(username=self.organiser.username,password="Password123")
        response = self.client.get(self.url)
        messages_list = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list),1)
        self.assertEqual(messages_list[0].level,messages.SUCCESS)
        self.assertTemplateUsed(response,'edit_meeting.html')

    def test_valid_title_change(self):
        self.client.login(username = self.owner.username,password="Password123")
        self.data['title'] = "New Meeting"
        response = self.client.post(self.url,self.data)
        
        self.assertContains(response,"New Meeting")
        self.assertContains(response,self.description)
        self.assertContains(response,self.location)
        self.assertContains(response,self.meetingtime)
        self.assertContains(response,self.type)
        self.assertContains(response,self.book)
        self.assertEqual(response.status_code,200)


    def test_valid_description_change(self):
        self.client.login(username = self.owner.username,password="Password123")
        self.data['description'] = "A whole new world"
        response = self.client.post(self.url,self.data)

        self.assertContains(response,self.title)
        self.assertContains(response,"A whole new world")
        self.assertContains(response,self.location)
        self.assertContains(response,self.meetingtime)
        self.assertContains(response,self.type)
        self.assertContains(response,self.book)
        self.assertEqual(response.status_code,200)

    def test_valid_location_change(self):
        self.client.login(username = self.owner.username,password="Password123")
        self.data['location'] = "A new place"
        response = self.client.post(self.url,self.data)

        self.assertContains(response,self.title)
        self.assertContains(response,self.description)
        self.assertContains(response,"A new place")
        self.assertContains(response,self.meetingtime)
        self.assertContains(response,self.type)
        self.assertContains(response,self.book)
        self.assertEqual(response.status_code,200)
    
    def test_valid_time_change(self):
        self.client.login(username = self.owner.username,password="Password123")
        self.data['meeting_time'] = "2022-12-25 14:00:00"
        response = self.client.post(self.url,self.data)

        self.assertContains(response,self.title)
        self.assertContains(response,self.description)
        self.assertContains(response,self.location)
        self.assertContains(response,"2022-12-25 14:00:00")
        self.assertContains(response,self.type)
        self.assertContains(response,self.book)
        self.assertEqual(response.status_code,200)

    def test_valid_type_change(self):
        self.client.login(username = self.owner.username,password="Password123")
        self.data['type'] = Meeting.MeetingType.SOCIAL
        response = self.client.post(self.url,self.data)

        self.assertContains(response,self.title)
        self.assertContains(response,self.description)
        self.assertContains(response,self.location)
        self.assertContains(response,self.meetingtime)
        self.assertContains(response,Meeting.MeetingType.SOCIAL)
        self.assertContains(response,self.book)
        self.assertEqual(response.status_code,200)

    def test_valid_book_change(self):
        self.client.login(username = self.owner.username,password="Password123")
        self.data['book'] = self.book2
        response = self.client.post(self.url,self.data)

        self.assertContains(response,self.title)
        self.assertContains(response,self.description)
        self.assertContains(response,self.location)
        self.assertContains(response,self.meetingtime)
        self.assertContains(response,self.type)
        self.assertContains(response,self.book2)
        self.assertEqual(response.status_code,200)

    #Test for redirect to meeting view 