"""Unit testing of the Agenda view."""
import datetime
import pytz

from django.test import TestCase, tag
from django.urls import reverse

from BookClub.models import User, Club, ClubMembership, Book, Meeting
from BookClub.tests.helpers import reverse_with_next


@tag('views', 'agenda')
class AgendaViewTestCase(TestCase):
    """Tests of the Agenda view."""
    fixtures = [
        "BookClub/tests/fixtures/default_users.json",
        "BookClub/tests/fixtures/default_clubs.json",
        "BookClub/tests/fixtures/default_books.json",
    ]

    def setUp(self):
        self.club = Club.objects.get(pk=1)
        self.book = Book.objects.get(pk=1)
        self.user = User.objects.get(pk=1)
        self.another_user = User.objects.get(pk=2)
        self.third_user = User.objects.get(pk=3)

        ClubMembership.objects.create(user=self.user, club=self.club, membership=ClubMembership.UserRoles.OWNER)
        ClubMembership.objects.create(user=self.another_user, club=self.club, membership=ClubMembership.UserRoles.MODERATOR)

        self.meeting_today = Meeting.objects.create(
            organiser=self.user,
            club=self.club,
            meeting_time=pytz.utc.localize(datetime.datetime.today()),
            meeting_end_time="9999-02-22T20:00+00:00",
            created_on="2022-02-10",
            location="Volts House",
            title="Sebs complete guide to CS",
            description="Freelo",
            type="B",
            book=self.book
        )
        self.meeting_future = Meeting.objects.create(
            organiser=self.user,
            club=self.club,
            meeting_time="9999-02-22T19:00+00:00",
            meeting_end_time="9999-02-22T20:00+00:00",
            created_on="0001-02-10",
            location="Amirs House",
            title="Guide to global",
            description="Amirs complete guide to becoming a role model entry fragger/star player/mvp/igl/glave wannabe/seb wannabe",
            type="B",
            book=self.book
        )
        self.meeting_not_joined_today = Meeting.objects.create(
            organiser=self.another_user,
            club=self.club,
            meeting_time=pytz.utc.localize(datetime.datetime.today()),
            meeting_end_time="9999-02-22T20:00+00:00",
            created_on="2022-02-10",
            location="Org",
            title="Fambit",
            description="Fambit looking for an org",
            type="B",
            book=self.book
        )

        self.meeting_not_joined_upcoming = Meeting.objects.create(
            organiser=self.another_user,
            club=self.club,
            meeting_time="9999-02-22T19:00+00:00",
            meeting_end_time="9999-02-22T20:00+00:00",
            created_on="2022-02-10",
            location="Aoba Johsai",
            title="Oikawas Dream",
            description="Amir + Oikawa",
            type="B",
            book=self.book
        )

        self.url = reverse('agenda')

    def test_url(self):
        url = reverse('agenda')
        self.assertEqual(url, '/agenda/')

    def test_view_agenda_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200, fetch_redirect_response=True)
        self.assertTemplateUsed(response, 'authentication/login.html')

    """Tests for users to see their agenda"""

    def test_user_can_see_agenda_for_joined_today(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'meeting/agenda.html')
        self.assertContains(response, "Today's Meetings")
        self.assertContains(response, "Sebs complete guide to CS")
        self.assertContains(response, "Freelo")
        self.assertContains(response, "Organised by <i>johndoe</i> for <i>Johnathan Club</i>")

    def test_user_can_see_agenda_for_joined_upcoming(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'meeting/agenda.html')
        self.assertContains(response, "Upcoming Meetings")
        self.assertContains(response, "Guide to global")
        self.assertContains(response, "Amirs complete guide to")
        self.assertContains(response, "Organised by <i>johndoe</i> for <i>Johnathan Club</i>")

    def test_user_can_see_agenda_for_not_joined_today(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'meeting/agenda.html')
        self.assertContains(response, "Today's Meetings")
        self.assertContains(response, "Fambit")
        self.assertContains(response, "Fambit looking for an org")
        self.assertContains(response, "Organised by <i>janedoe</i> for <i>Johnathan Club</i>")

    def test_user_can_see_agenda_for_not_joined_upcoming(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'meeting/agenda.html')
        self.assertContains(response, "Upcoming Meetings")
        self.assertContains(response, "Oikawas Dream")
        self.assertContains(response, "Amir + Oikawa")
        self.assertContains(response, "Organised by <i>janedoe</i> for <i>Johnathan Club</i>")

    def test_user_can_see_agenda_for_both(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'meeting/agenda.html')
        self.assertContains(response, "Today's Meetings")
        self.assertContains(response, "Upcoming Meetings")

    '''Tests for users to not see another club agenda'''

    def test_user_cannot_see_agenda_for_a_club_they_are_not_in_joined_today(self):
        self.client.login(username=self.third_user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'meeting/agenda.html')
        self.assertContains(response, "Today's Meetings")
        self.assertNotContains(response, "Sebs complete guide to CS")
        self.assertNotContains(response, "Freelo")
        self.assertNotContains(response, "Organised by <i>johndoe</i> for <i>Johnathan Club</i>")

    def test_user_cannot_see_agenda_for_a_club_they_are_not_in_upcoming_today(self):
        self.client.login(username=self.third_user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'meeting/agenda.html')
        self.assertContains(response, "Upcoming Meetings")
        self.assertNotContains(response, "Guide to global")
        self.assertNotContains(response, "Amirs complete guide to becoming a role model entry fragger/star player/mvp/igl/glave wannabe/seb wannabe")
        self.assertNotContains(response, "Organised by <i>johndoe</i> for <i>Johnathan Club</i>")

    def test_user_cannot_see_agenda_for_a_club_they_are_not_in_not_joined_today(self):
        self.client.login(username=self.third_user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'meeting/agenda.html')
        self.assertContains(response, "Today's Meetings")
        self.assertNotContains(response, "Fambit")
        self.assertNotContains(response, "Fambit looking for an org")
        self.assertNotContains(response, "Organised by <i>janedoe</i> for <i>Johnathan Club</i>")

    def test_user_cannot_see_agenda_for_a_club_they_are_not_in_for_not_upcoming(self):
        self.client.login(username=self.third_user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'meeting/agenda.html')
        self.assertContains(response, "Upcoming Meetings")
        self.assertNotContains(response, "Oikawas Dream")
        self.assertNotContains(response, "Amir + Oikawa")
        self.assertNotContains(response, "Organised by <i>janedoe</i> for <i>Johnathan Club</i>")
