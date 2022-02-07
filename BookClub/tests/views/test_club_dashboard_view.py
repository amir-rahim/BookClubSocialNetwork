"""Unit tests of the club dashboard view."""
from django.test import TestCase
from BookClub.models import Club, ClubMembership, User
from django.urls import reverse
from BookClub.tests.helpers import reverse_with_next


class ClubDashboardViewTest(TestCase):
    """Unit tests of the club page view."""
    fixtures = [
        "BookClub/tests/fixtures/default_users.json",
        "BookClub/tests/fixtures/default_clubs.json",
        "BookClub/tests/fixtures/default_memberships.json"
    ]

    def setUp(self):
        self.user = User.objects.get(email="johndoe@example.com")
        self.jane = User.objects.get(email="janedoe@example.com")
        self.club = Club.objects.get(name="Lit Masterpiece")
        self.url = reverse("club_dashboard", kwargs={"club_id": self.club.id})
        self.owner = self.club.get_owner()

    def test_club_dashboard_url(self):
        self.assertEqual(self.url, f"/club_dashboard/")

    def test_club_dashboard_has_club_info(self):
        self.client.login(username=self.user.email, password="Password123")
        url = reverse("club_dashboard", kwargs={"club_id": self.club.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "club_dashboard.html")
        self.assertContains(response, "Lit Masterpiece")
        self.assertContains(response, "This is the first club")
        self.assertContains(response, "2022-02-06")
        self.assertContains(response, "Keep reading")

    def test_club_dashboard_has_club_stats(self):
        self.client.login(username=self.user.email, password="Password123")
        url = reverse("club_dashboard", kwargs={"club_id": self.club.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "club_dashboard.html")
        self.assertContains(response, self.club.get_number_of_members())
        self.assertContains(response, self.club.get_number_of_meetings())
        self.assertContains(response, self.club.get_number_of_posts())
        self.assertContains(response, self.club.get_review_score())

    def test_club_dashboard_has_owner_info(self):
        self.client.login(username=self.user.email, password="Password123")
        url = reverse("club_dashboard", kwargs={"club_id": self.club.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "club_dashboard.html")
        self.assertTemplateUsed(response, "janedoe")
        self.assertContains(response, "janedoe@example.com")
