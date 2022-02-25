"""Tests of the available_clubs view."""
from django.test import TestCase
from django.urls import reverse
from BookClub.models import User, Club, ClubMembership


class AvailableClubsViewTestCase(TestCase):
    """Tests of the available_clubs view."""

    fixtures = [
        'BookClub/tests/fixtures/default_users.json',
        'BookClub/tests/fixtures/default_clubs.json',
        'BookClub/tests/fixtures/default_club_owners.json',
    ]

    def setUp(self):
        self.url = reverse('available_clubs')
        self.user = User.objects.get(username="johndoe")

    def test_url(self):
        self.assertEqual(self.url,'/club/')

    def test_get_template_logged_in(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'available_clubs.html')

    def test_redirect_when_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_no_club(self):
        self.client.login(username=self.user.username, password='Password123')
        membership1 = ClubMembership.objects.create(user=self.user, club=Club.objects.get(name="Jeannette Club"), membership=ClubMembership.UserRoles.MEMBER)
        membership1.save()
        membership2 = ClubMembership.objects.create(user=self.user, club=Club.objects.get(name="Jack Club"), membership=ClubMembership.UserRoles.MEMBER)
        membership2.save()
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'available_clubs.html')
        clubs = list(response.context['clubs'])
        self.assertEqual(len(clubs), 0)
        self.assertContains(response, "<p style=\"text-align: center\">There are no available clubs at the moment.</p>")

    def test_contains_club_not_member_of(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'available_clubs.html')
        clubs = list(response.context['clubs'])
        self.assertIn(Club.objects.get(name="Jeannette Club"), clubs)
        self.assertContains(response, "<td>Jeannette Club</td>")

    def test_not_contains_club_member_of(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'available_clubs.html')
        clubs = list(response.context['clubs'])
        self.assertNotIn(Club.objects.get(name="Johnathan Club"), clubs)
        self.assertNotContains(response, "<td>Johnathan Club</td>")

    def test_contains_club_is_applicant(self):
        self.client.login(username=self.user.username, password='Password123')
        new_membership = ClubMembership.objects.create(user=self.user, club=Club.objects.get(name="Jeannette Club"), membership=ClubMembership.UserRoles.APPLICANT)
        new_membership.save()
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'available_clubs.html')
        clubs = list(response.context['clubs'])
        self.assertIn(Club.objects.get(name="Jeannette Club"), clubs)
        self.assertContains(response, "<td>Jeannette Club</td>")

    def test_can_contain_multiple_clubs(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'available_clubs.html')
        clubs = list(response.context['clubs'])
        self.assertEqual(len(clubs), 2)
