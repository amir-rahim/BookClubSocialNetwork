"""Tests of the Member List view."""
from django.test import TestCase, tag
from django.urls import reverse
from django.contrib import messages
from django.contrib.messages import get_messages
from django.core.exceptions import ObjectDoesNotExist

from BookClub.models import User, Club, ClubMembership


@tag('club', 'member_list')
class MemberListTestCase(TestCase):
    """Tests of the Member List view."""

    fixtures = [
        'BookClub/tests/fixtures/default_users.json',
        'BookClub/tests/fixtures/default_clubs.json',
        'BookClub/tests/fixtures/default_memberships.json',
    ]

    def setUp(self):
        self.club = Club.objects.get(pk=1)
        self.private_club = Club.objects.get(pk=3)
        self.url = reverse('member_list', kwargs={'club_url_name': self.club.club_url_name})
        self.user = User.objects.get(username="johndoe")
        self.jack = User.objects.get(username="jackdoe")
        self.jane = User.objects.get(username="janedoe")
        self.owner = Club.objects.get(pk=1).get_owner()[0]
        self.moderators = Club.objects.get(pk=1).get_moderators()
        self.members = Club.objects.get(pk=1).get_members()
        self.applicants = Club.objects.get(pk=1).get_applicants()

    def test_url(self):
        url = reverse('member_list', kwargs={'club_url_name': self.club.club_url_name})
        self.assertEqual(url, '/club/' + self.club.club_url_name + '/members/')

    def test_get_template_logged_in(self):
        self.client.login(username=self.user.username, password="Password123")
        url = reverse('member_list', kwargs={'club_url_name': self.club.club_url_name})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'clubs/club_members.html')

    def test_redirect_when_not_logged_in(self):
        url = reverse('member_list', kwargs={'club_url_name': self.club.club_url_name})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_non_member_can_view_member_list(self):
        non_member = User.objects.get(pk=6)
        self.client.login(username=non_member.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'clubs/club_members.html')

    def test_redirect_if_not_member_of_club_private(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(reverse("member_list", kwargs={"club_url_name": self.private_club.club_url_name}))
        self.assertRedirects(response, expected_url=reverse("club_dashboard", kwargs={"club_url_name": self.private_club.club_url_name}), status_code=302, target_status_code=302)
        messages_list = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        self.assertEqual(str(messages_list[0]),"This club is private")
    
    def test_invalid_club(self):
        self.client.login(username=self.jack.username, password="Password123")
        response = self.client.get(reverse("member_list", kwargs={"club_url_name": 'fakeclub'}))
        self.assertRedirects(response, expected_url=reverse("club_dashboard", kwargs={"club_url_name": 'fakeclub'}), status_code=302, target_status_code=302)

    """ Tests to see what information is displayed """

    def test_can_see_club_name(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'clubs/club_members.html')
        self.assertContains(response, self.club.name)

    def test_owner_has_admin_options(self):
        self.client.login(username=self.jane.username, password="Password123")
        url = reverse('member_list', kwargs={'club_url_name': self.club.club_url_name})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'clubs/club_members.html')
        self.assertContains(response, "Club Administration")
        self.assertContains(response, "Manage Club")

    def test_mod_has_no_admin_options(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'clubs/club_members.html')
        self.assertContains(response, "Club Administration")
        self.assertNotContains(response, "Manage Club")

    def test_member_has_no_admin_options(self):
        self.client.login(username=self.jack.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'clubs/club_members.html')
        self.assertNotContains(response, "Club Administration")
        self.assertNotContains(response, "Manage Club")

    def test_can_see_owner(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'clubs/club_members.html')
        self.assertContains(response, self.owner.username)
        self.assertContains(response, self.owner.public_bio)

    def test_can_see_mods(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'clubs/club_members.html')
        for mod in self.moderators:
            self.assertContains(response, mod.username)

    def test_can_see_members(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'clubs/club_members.html')
        for member in self.members:
            self.assertContains(response, member.username)

    def test_cannot_see_applicants(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'clubs/club_members.html')
        for applicant in self.applicants:
            self.assertNotContains(response, applicant.username)

    def test_owner_is_visible(self):
        self.client.login(username=self.jack.username, password="Password123")
        example_club = Club.objects.create(name="Example", club_url_name="example", description="Example Club",
                                           tagline="Welcome", rules="None")
        example_owner = ClubMembership.objects.create(club=example_club, user=self.jack, membership=2)
        url = reverse("member_list", kwargs={"club_url_name": example_club.club_url_name})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'clubs/club_members.html')
        self.assertContains(response, "<b>Name: </b> " + self.jack.username)
        self.assertContains(response, "<b>Public Bio: </b> " + self.jack.public_bio)

    def test_no_moderators(self):
        self.client.login(username=self.jack.username, password="Password123")
        example_club = Club.objects.create(name="Example", club_url_name="example", description="Example Club",
                                           tagline="Welcome", rules="None")
        example_owner = ClubMembership.objects.create(club=example_club, user=self.jack, membership=2)
        url = reverse("member_list", kwargs={"club_url_name": example_club.club_url_name})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'clubs/club_members.html')
        self.assertContains(response, "There are no moderators in this club.")

    def test_no_members(self):
        self.client.login(username=self.jack.username, password="Password123")
        example_club = Club.objects.create(name="Example", club_url_name="example", description="Example Club",
                                           tagline="Welcome", rules="None")
        example_owner = ClubMembership.objects.create(club=example_club, user=self.jack, membership=2)
        url = reverse("member_list", kwargs={"club_url_name": example_club.club_url_name})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'clubs/club_members.html')
        self.assertContains(response, "There are no members in this club.")
