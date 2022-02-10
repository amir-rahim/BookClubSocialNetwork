from urllib import request, response
from django.test import RequestFactory,TestCase
from BookClub.tests.helpers import reverse_with_next
from django.urls import reverse
from BookClub.views import delete_club
from BookClub.models import *

class DeleteClubTest(TestCase):

    fixtures = ['default_club_members.json','default_club_owners.json','default_clubs.json','default_memberships.json','BookClub\tests\fixtures\default_users.json']
    def setUp(self):
        super(TestCase,self).setUp()
        self.user1 = User.objects.get(pk=1)
        self.club = Club.objects.get(pk=1)
        self.owner = ClubMembership.objects.create(
            user = self.user1,club = self.club,
            membership = ClubMembership.UserRoles.OWNER
         )

        self.user2 = User.objects.get(pk=2)
        self.moderator = ClubMembership.objects.create(
            user = self.user2,club = self.club,
            membership = ClubMembership.UserRoles.MODERATOR
        )
        self.user3 = User.objects.get(pk=3)
        self.member = ClubMembership.objects.create(
            user = self.user3,club = self.club,
            membership = ClubMembership.UserRoles.MEMBER
        )
        self.user4 = User.objects.get(pk=4)
        self.applicant = ClubMembership.objects.create(
            user = self.user3,club = self.club,
            membership = ClubMembership.UserRoles.APPLICANT
        )
        self.url = reverse("delete_club.html")

        
        
    def test_delete_club_url(self):
        self.assertEqual(self.url,'delete_club/')


    def test_delete_club_not_logged_in(self):
        #Not sure  what page to use reverse_with_next with 
        redirect_url = reverse_with_next('delete_club', self.url)
        response = self.client.post(self.url, self.data, follow=True)
        self.assertRedirects(response, redirect_url,
            status_code=302, target_status_code=200, fetch_redirect_response=True
        )
        self.assertTemplateUsed(response, 'delete_club.html')

    def test_owner_can_delete_club(self):
        self.client.login(username=self.owner.username, password = "Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,"delete_club.html")
        self.assertEqual(self.club,None)

    def test_moderator_cannot_delete_club(self):
        self.client.login(username=self.moderator.username, password = "Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code,302)
        self.assertRedirects(response,'available_clubs.html',status_code=302)
        self.assertTemplateNotUsed(response,'delete_club.html')
        
    
    def test_member_cannot_delete_club(self):
        self.client.login(username=self.member.username, password = "Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code,302)
        self.assertRedirects(response,'available_clubs.html',status_code=302)
        self.assertTemplateNotUsed(response,'delete_club.html')

    def test_applicant_cannot_delete_club(self):
        self.client.login(username=self.applicant.username, password = "Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code,302)
        self.assertRedirects(response,'available_clubs.html',status_code=302)
        self.assertTemplateNotUsed(response,'delete_club.html')


    # def test(self):
    #     request = RequestFactory().get('delete_club/')
    #     view = delete_club()
    #     view.setUp(request)


