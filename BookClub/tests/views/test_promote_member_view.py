# """Tests of the Promote Member view."""
# from django.test import TestCase
# from django.urls import reverse
# from django.contrib import messages
# from django.core.exceptions import ObjectDoesNotExist
# from BookClub.models import User, Club, ClubMembership
#
#
# class PromoteMemberView(TestCase):
#     """Tests of the Promote Member view."""
# 
#     fixtures = [
#         'BookClub/tests/fixtures/default_users.json',
#         'BookClub/tests/fixtures/default_clubs.json',
#     ]
#
#     def setUp(self):
#         self.owner = User.objects.get(pk=1)
#         self.moderator = User.objects.get(pk=2)
#         self.member = User.objects.get(pk=3)
#         self.applicant = User.objects.get(pk=4)
#         self.club = Club.objects.get(pk="1")
#
#         ClubMembership.objects.create(user=self.owner, club=self.club, membership=ClubMembership.UserRoles.OWNER)
#         ClubMembership.objects.create(user=self.moderator, club=self.club, membership=ClubMembership.UserRoles.MODERATOR)
#         ClubMembership.objects.create(user=self.member, club=self.club, membership=ClubMembership.UserRoles.MEMBER)
#         ClubMembership.objects.create(user=self.applicant, club=self.club, membership=ClubMembership.UserRoles.APPLICANT)
#
#         self.url = reverse('promote_member', kwargs={'url_name': self.club.url_name, 'id': self.member.id})
#
#     def test_promote_member_url(self):
#         self.assertEqual(self.url, f'/promote_member/{self.club.url_name}/{self.member.id}')
#
#     def test_redirect_when_not_logged_in(self):
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, 302)
#
#     def test_owner_can_promote_member(self):
#         self.client.login(username=self.owner.username, password='Password123')
#         self.assertTrue(ClubMembership.objects.filter(user=self.member, club=self.club, membership=ClubMembership.UserRoles.MEMBER).exists())
#         response = self.client.get(self.url)
#         self.assertTrue(ClubMembership.objects.filter(user=self.member, club=self.club, membership=ClubMembership.UserRoles.MODERATOR).exists())
