"""Unit testing of the my_club_memberships view."""
from django.test import TestCase, tag
from django.urls import reverse

from BookClub.models import User, Club, ClubMembership


@tag('views', 'club', 'membership_list')
class MyClubsMembershipsViewTestCase(TestCase):
    """Tests of the my_club_memberships view."""

    fixtures = [
        'BookClub/tests/fixtures/default_users.json',
        'BookClub/tests/fixtures/default_clubs.json',
        'BookClub/tests/fixtures/default_club_owners.json',
    ]

    def setUp(self):
        self.url = reverse('my_club_memberships')
        self.user = User.objects.get(username="johndoe")

    def test_url(self):
        self.assertEqual(self.url, '/memberships/')

    def test_get_template_logged_in(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'clubs/my_club_memberships.html')

    def test_redirect_when_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_no_club(self):
        self.client.login(username=self.user.username, password='Password123')
        user2 = User.objects.get(username="janedoe")
        membership = ClubMembership.objects.filter(pk=1).update(user=user2)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'clubs/my_club_memberships.html')
        clubs = list(response.context['clubs'])
        self.assertEqual(len(clubs), 0)
        self.assertContains(response,
                            "You are not a member of any club, you can find clubs <a href=\"/club/\" class=\"is-link\"><i>here</i></a>.")

    def test_not_contains_club_not_member_of(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'clubs/my_club_memberships.html')
        clubs = list(response.context['clubs'])
        self.assertNotIn(Club.objects.get(name="Jeannette Club"), clubs)
        self.assertNotContains(response, "<td>Jeannettes Club</td>")

    def test_contains_club_member_of(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'clubs/my_club_memberships.html')
        clubs = list(response.context['clubs'])
        self.assertIn(Club.objects.get(name="Johnathan Club"), clubs)
        self.assertContains(response, "<td>Johnathan Club</td>")

    def test_not_contains_club_is_applicant(self):
        self.client.login(username=self.user.username, password='Password123')
        new_membership = ClubMembership.objects.create(user=self.user, club=Club.objects.get(name="Jeannette Club"),
                                                       membership=ClubMembership.UserRoles.APPLICANT)
        new_membership.save()
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'clubs/my_club_memberships.html')
        clubs = list(response.context['clubs'])
        self.assertNotIn(Club.objects.get(name="Jeannette Club"), clubs)
        self.assertNotContains(response, "<td>Jeannette Club</td>")

    def test_can_contain_multiple_clubs(self):
        self.client.login(username=self.user.username, password='Password123')
        new_membership = ClubMembership.objects.create(user=self.user, club=Club.objects.get(name="Jeannette Club"),
                                                       membership=ClubMembership.UserRoles.MEMBER)
        new_membership.save()
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'clubs/my_club_memberships.html')
        clubs = list(response.context['clubs'])
        self.assertEqual(len(clubs), 2)
