"""Tests of the applications list view."""
from django.test import TestCase, tag
from django.urls import reverse

from BookClub.models import User, Club, ClubMembership


@tag('club', 'applications_list')
class MyClubsMembershipsViewTestCase(TestCase):
    """Tests of the applications list view."""

    fixtures = [
        'BookClub/tests/fixtures/default_users.json',
        'BookClub/tests/fixtures/default_clubs.json',
        'BookClub/tests/fixtures/default_memberships.json',
    ]

    def setUp(self):
        self.url = reverse('applications')
        # Applicant of club 1
        self.applicant = User.objects.get(pk=4)
        # Owner of club 1
        self.owner = User.objects.get(pk=2)
        # Moderator of club 1
        self.mod = User.objects.get(pk=1)
        # Member of club 1
        self.member = User.objects.get(pk=6)

    def test_url(self):
        self.assertEqual(self.url, '/applications/')

    def test_get_template_logged_in(self):
        self.client.login(username=self.applicant.username, password="Password123")
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'applications_list.html')

    def test_redirect_when_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    """Testing each role type"""

    def test_member_has_no_applications(self):
        self.client.login(username=self.member.username, password='Password123')
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'applications_list.html')
        clubs = list(response.context['clubs'])
        self.assertEqual(len(clubs), 0)
        self.assertContains(response,
                            "You have not applied to any clubs yet, find more <a href=\"/club/\" class=\"is-link\"><i>here</i></a>.")

    def test_owner_has_no_applications(self):
        self.client.login(username=self.owner.username, password='Password123')
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'applications_list.html')
        clubs = list(response.context['clubs'])
        self.assertEqual(len(clubs), 0)
        self.assertContains(response,
                            "You have not applied to any clubs yet, find more <a href=\"/club/\" class=\"is-link\"><i>here</i></a>.")

    def test_moderator_has_no_applications(self):
        self.client.login(username=self.mod.username, password='Password123')
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'applications_list.html')
        clubs = list(response.context['clubs'])
        self.assertEqual(len(clubs), 0)
        self.assertContains(response,
                            "You have not applied to any clubs yet, find more <a href=\"/club/\" class=\"is-link\"><i>here</i></a>.")
    
    """Testing table contents"""

    def test_contains_club_of_application(self):
        self.client.login(username=self.applicant.username, password='Password123')
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'applications_list.html')
        clubs = list(response.context['clubs'])
        self.assertIn(Club.objects.get(pk=1), clubs)
        self.assertContains(response, "<td>Johnathan Club</td>")

    def test_can_contain_multiple_clubs(self):
        self.client.login(username=self.applicant.username, password='Password123')
        new_membership = ClubMembership.objects.create(user=self.applicant, club=Club.objects.get(pk=2),
                                                       membership=ClubMembership.UserRoles.APPLICANT)
        new_membership.save()
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'applications_list.html')
        clubs = list(response.context['clubs'])
        self.assertEqual(len(clubs), 2)
