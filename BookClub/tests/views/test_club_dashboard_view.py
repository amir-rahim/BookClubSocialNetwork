"""Unit tests of the club dashboard view."""
from django.test import TestCase
from BookClub.models import Club, User, ClubMembership
from django.urls import reverse
from BookClub.tests.helpers import reverse_with_next
from django.test import Client


class ClubDashboardViewTest(TestCase):
    """Unit tests of the club page view."""
    fixtures = [
        "BookClub/tests/fixtures/default_users.json",
        "BookClub/tests/fixtures/default_clubs.json",
        "BookClub/tests/fixtures/default_memberships.json"
    ]

    def setUp(self):
        self.user = User.objects.get(username="johndoe")
        self.jane = User.objects.get(username="janedoe")
        self.jack = User.objects.get(username="jackdoe")
        self.club = Club.objects.get(name="Johnathan Club")
        self.url = reverse("club_dashboard", kwargs={"club_name": self.club.name})
        self.private_club = Club.objects.get(name="Jack Club")
        self.private_url = reverse("available_clubs")


    def test_club_dashboard_url(self):
        self.assertEqual(self.url, f"/club/Johnathan%20Club/")

    def test_club_dashboard_has_club_info(self):
        self.client.login(username=self.user.username, password="Password123")
        url = reverse("club_dashboard", kwargs={"club_name": self.club.name})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "club_dashboard.html")
        self.assertContains(response, "Johnathan Club")
        self.assertContains(response, "This is a very cool club that is owned by a certain Johnathan. Reading certain books...")
        self.assertContains(response, "Welcome to Johnathan&#x27;s club! We read the best books!!!")
        self.assertContains(response, "Don&#x27;t be annoying")
        self.assertContains(response, "Feb. 4, 2022")

    # Cannot be fully tested as some models have not yet been implemented
    def test_club_dashboard_has_club_stats(self):
        self.client.login(username=self.user.username, password="Password123")
        url = reverse("club_dashboard", kwargs={"club_name": self.club.name})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "club_dashboard.html")
        # self.assertContains(response, self.club.get_number_of_members())
        # self.assertContains(response, self.club.get_number_of_meetings())
        # self.assertContains(response, self.club.get_number_of_posts())
        # self.assertContains(response, self.club.get_review_score())

    def test_club_dashboard_has_owner_info(self):
        self.client.login(username=self.user.username, password="Password123")
        url = reverse("club_dashboard", kwargs={"club_name": self.club.name})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "club_dashboard.html")
        self.assertContains(response, "janedoe")
        self.assertContains(response, "janedoe@example.com")

    def test_redirect_if_not_member_of_club_private(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(reverse("club_dashboard", kwargs={"club_name": self.private_club.name}))
        self.assertRedirects(response, expected_url=reverse("available_clubs"), status_code=302, target_status_code=200)


    def test_private_club_member_can_view_dashboard(self):
        self.client.login(username=self.jane.username, password="Password123")
        url = reverse("club_dashboard", kwargs={"club_name": self.private_club.name})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "club_dashboard.html")


    def test_owner_has_admin_options(self):
        self.client.login(username=self.jane.username, password="Password123")
        url = reverse("club_dashboard", kwargs={"club_name": self.club.name})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "club_dashboard.html")
        self.assertContains(response, "Club Administration")
        self.assertContains(response, "Manage Club")
        self.assertContains(response, "Club Settings")

    def test_mod_has_no_admin_options(self):
        self.client.login(username=self.user.username, password="Password123")
        url = reverse("club_dashboard", kwargs={"club_name": self.club.name})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "club_dashboard.html")
        self.assertNotContains(response, "Club Administration")
        self.assertNotContains(response, "Manage Club")
        self.assertNotContains(response, "Club Settings")
    
    def test_member_has_no_admin_options(self):
        self.client.login(username=self.jack.username, password="Password123")
        url = reverse("club_dashboard", kwargs={"club_name": self.club.name})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "club_dashboard.html")
        self.assertNotContains(response, "Club Administration")
        self.assertNotContains(response, "Manage Club")
        self.assertNotContains(response, "Club Settings")
