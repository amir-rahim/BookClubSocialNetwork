"""Tests of the Applicant List view."""
from django.test import TestCase, tag
from django.urls import reverse

from BookClub.models import User, Club


@tag('club', 'applicant_list')
class ApplicantListTestCase(TestCase):
    """Tests of the Applicant List view."""

    fixtures = [
        'BookClub/tests/fixtures/default_users.json',
        'BookClub/tests/fixtures/default_clubs.json',
        'BookClub/tests/fixtures/default_memberships.json',
    ]

    def setUp(self):
        self.club = Club.objects.get(pk=1)
        self.url = reverse('applicant_list', kwargs={'club_url_name': self.club.club_url_name})
        self.user = User.objects.get(username="johndoe")
        self.jack = User.objects.get(username="jackdoe")
        self.jane = User.objects.get(username="janedoe")
        self.owner = Club.objects.get(pk=1).get_owner()[0]
        self.moderators = Club.objects.get(pk=1).get_moderators()
        self.members = Club.objects.get(pk=1).get_members()
        self.applicants = Club.objects.get(pk=1).get_applicants()

    def test_url(self):
        url = reverse('applicant_list', kwargs={'club_url_name': self.club.club_url_name})
        self.assertEqual(url, '/club/' + self.club.club_url_name + '/applicants/')

    def test_get_template_logged_in(self):
        self.client.login(username=self.user.username, password="Password123")
        url = reverse('applicant_list', kwargs={'club_url_name': self.club.club_url_name})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'applicant_list.html')

    def test_redirect_when_not_logged_in(self):
        url = reverse('applicant_list', kwargs={'club_url_name': self.club.club_url_name})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_can_see_club_name(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'applicant_list.html')
        self.assertContains(response, self.club.name)

    def test_owner_has_admin_options(self):
        self.client.login(username=self.jane.username, password="Password123")
        url = reverse('applicant_list', kwargs={'club_url_name': self.club.club_url_name})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'applicant_list.html')
        self.assertContains(response, "Club Administration")
        self.assertContains(response, "Manage Club")
        self.assertContains(response, "Club Settings")

    def test_mod_has_no_admin_options(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'applicant_list.html')
        self.assertNotContains(response, "Club Administration")
        self.assertNotContains(response, "Manage Club")
        self.assertNotContains(response, "Club Settings")

    def test_member_redirects(self):
        self.client.login(username=self.jack.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertTemplateNotUsed(response, 'applicant_list.html')

    def test_applicant_redirects(self):
        self.client.login(username=self.applicants[0].username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertTemplateNotUsed(response, 'applicant_list.html')

    def test_cant_see_owner(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'applicant_list.html')
        self.assertNotContains(response, self.owner.username)

    def test_cant_see_mods(self):
        self.client.login(username=self.jane.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'applicant_list.html')
        for mod in self.moderators:
            self.assertNotContains(response, mod.username)

    def test_cant_see_members(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'applicant_list.html')
        for member in self.members:
            self.assertNotContains(response, member.username)

    def test_can_see_applicants(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'applicant_list.html')
        for applicant in self.applicants:
            self.assertContains(response, applicant.username)

    def test_owner_can_see_view_button(self):
        self.client.login(username=self.jane.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'applicant_list.html')
        self.assertContains(response, "View")

    def test_mod_can_see_view_button(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'applicant_list.html')
        self.assertContains(response, "View")

    def test_owner_can_see_approve_button(self):
        self.client.login(username=self.jane.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'applicant_list.html')
        self.assertContains(response, "Approve")

    def test_mod_can_see_approve_button(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'applicant_list.html')
        self.assertContains(response, "Approve")

    def test_owner_can_see_reject_button(self):
        self.client.login(username=self.jane.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'applicant_list.html')
        self.assertContains(response, "Reject")

    def test_mod_can_see_reject_button(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'applicant_list.html')
        self.assertContains(response, "Reject")
