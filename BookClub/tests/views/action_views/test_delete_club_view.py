from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase, tag
from django.urls import reverse

from BookClub.models import Club, ClubMembership, User
from BookClub.tests.helpers import LogInTester


@tag("views", "action_views", "delete_club")
class DeleteClubTest(TestCase, LogInTester):
    fixtures = [
        'BookClub/tests/fixtures/default_clubs.json',
        'BookClub/tests/fixtures/default_users.json']

    def setUp(self):
        super(TestCase, self).setUp()
        self.user1 = User.objects.get(pk=1)
        self.club = Club.objects.get(pk=1)
        self.owner = ClubMembership.objects.create(
            user=self.user1, club=self.club,
            membership=ClubMembership.UserRoles.OWNER
        )

        self.user2 = User.objects.get(pk=2)
        self.moderator = ClubMembership.objects.create(
            user=self.user2, club=self.club,
            membership=ClubMembership.UserRoles.MODERATOR
        )
        self.user3 = User.objects.get(pk=3)
        self.member = ClubMembership.objects.create(
            user=self.user3, club=self.club,
            membership=ClubMembership.UserRoles.MEMBER
        )
        self.user4 = User.objects.get(pk=4)
        self.applicant = ClubMembership.objects.create(
            user=self.user4, club=self.club,
            membership=ClubMembership.UserRoles.APPLICANT
        )
        self.url = reverse("delete_club", kwargs={"club_url_name": self.club.club_url_name})

    def test_delete_club_url(self):
        self.assertEqual(self.url, f'/delete_club/{self.club.club_url_name}/')

    def test_delete_club_not_logged_in_redirect(self):
        """Test for a guest unsuccessfully trying to delete a club"""
        self.assertFalse(self._is_logged_in())
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        self.client.post(self.url)

        club_exists_before = Club.objects.filter(pk=self.club.id).exists()
        self.assertEqual(club_exists_before, True)
        club_exists_after = Club.objects.filter(pk=self.club.id).exists()
        self.assertEqual(club_exists_before, club_exists_after)

    def test_owner_can_delete_club(self):
        self.client.login(username=self.owner.user.username, password="Password123")
        self.assertTrue(self._is_logged_in())
        clubid = self.club.id
        club_exists_before = Club.objects.filter(pk=clubid).exists()
        self.assertEqual(club_exists_before, True)
        response = self.client.post(self.url)
        self.assertRedirects(response, f'/club/')
        self.assertEqual(response.status_code, 302)
        club_exists_after = Club.objects.filter(pk=clubid).exists()
        self.assertEqual(club_exists_after, False)

    def test_moderator_cannot_delete_club(self):
        self.client.login(username=self.moderator.user.username, password="Password123")
        self.assertTrue(self._is_logged_in())
        club_exists_before = Club.objects.filter(pk=self.club.id).exists()
        self.assertEqual(club_exists_before, True)
        response = self.client.post(self.url)
        self.assertRedirects(response, '/')
        self.assertEqual(response.status_code, 302)
        club_exists_after = Club.objects.filter(pk=self.club.id).exists()
        self.assertEqual(club_exists_before, club_exists_after)

    def test_member_cannot_delete_club(self):
        self.client.login(username=self.member.user.username, password="Password123")
        self.assertTrue(self._is_logged_in())
        club_exists_before = Club.objects.filter(pk=self.club.id).exists()
        self.assertEqual(club_exists_before, True)
        response = self.client.post(self.url)
        self.assertRedirects(response, '/')
        self.assertEqual(response.status_code, 302)
        club_exists_after = Club.objects.filter(pk=self.club.id).exists()
        self.assertEqual(club_exists_before, club_exists_after)

    def test_applicant_cannot_delete_club(self):
        self.client.login(username=self.applicant.user.username, password="Password123")
        self.assertTrue(self._is_logged_in())
        club_exists_before = Club.objects.filter(pk=self.club.id).exists()
        self.assertEqual(club_exists_before, True)
        response = self.client.post(self.url)
        self.assertRedirects(response, '/')
        self.assertEqual(response.status_code, 302)
        club_exists_after = Club.objects.filter(pk=self.club.id).exists()
        self.assertEqual(club_exists_before, club_exists_after)

    def test_owner_delete_invalid_club(self):
        self.client.login(username=self.owner.user.username, password='Password123')
        response = self.client.post(reverse('delete_club', kwargs={'club_url_name': "wrong"}))
        redirect_url = '/'
        with self.assertRaises(ObjectDoesNotExist):
            Club.objects.get(club_url_name="wrong").exists()

        response_message = self.client.get(redirect_url)
        messages_list = list(response_message.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    # Possible test: delete another club's club
