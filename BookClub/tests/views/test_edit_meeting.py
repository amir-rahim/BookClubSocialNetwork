from datetime import date, datetime
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
        self.owner = User.objects.get(username='johndoe')
        self.applicant = User.objects.get(username='janedoe')
        self.member = User.objects.get(username='jackdoe')
        self.club = Club.objects.get(pk=1)

        ClubMembership.objects.create(user = self.owner, club = self.club, membership = ClubMembership.UserRoles.OWNER)
        ClubMembership.objects.create(user = self.applicant, club = self.club, membership = ClubMembership.UserRoles.APPLICANT)
        ClubMembership.objects.create(user = self.member, club = self.club, membership = ClubMembership.UserRoles.MEMBER)
       
        
        self.book = Book.objects.get(pk=1)
        self.meeting = Meeting.objects.get(pk=1)
        
        self.url = reverse('edit_meeting', kwargs = {'club_url_name': self.club.club_url_name,'meeting_id':self.meeting.id})
        self.title = "new title"
        self.description = "this is the new description"
        self.location = "somewhere"
        self.meetingtime = datetime.now()
        self.created = datetime(2022,2,22,15)
        self.data = {
            'title': self.title,
            'description': self.description,
            'location': self.location,
            'meeting_time': self.meetingtime,
            'created_on': self.created,
            'type': Meeting.MeetingType.OTHER,
            'book': self.book
        }
    def test_edit_meeting_url(self):
        self.assertEqual(self.url,f'/club/{self.club.club_url_name}/meetings/{self.meeting.id}/edit/')