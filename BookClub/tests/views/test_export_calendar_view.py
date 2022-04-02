"""Unit testing of the Export Calendar view."""
from django.test import TestCase, tag
from django.urls import reverse
from django.contrib import messages
from BookClub.models import User, Club, ClubMembership, Book, Meeting

@tag('agenda')
class ExportCalendarViewTestCase(TestCase):
    """Tests of the Export Calendar view."""

    fixtures = [
        "BookClub/tests/fixtures/default_users.json",
        "BookClub/tests/fixtures/default_clubs.json",
        "BookClub/tests/fixtures/default_books.json",
    ]

    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.club = Club.objects.get(pk=1)
        self.book = Book.objects.get(pk=1)
        self.url = reverse('agenda_export')
        ClubMembership.objects.create(user=self.user, club=self.club, membership=ClubMembership.UserRoles.OWNER)

        self.meeting = Meeting.objects.create(
            organiser=self.user,
            club=self.club,
            meeting_time="9999-02-22T19:00+00:00",
            meeting_end_time="9999-02-22T20:00+00:00",
            created_on="2022-02-10",
            location="Bush House",
            title="Catch up",
            description="In this meeting we will be covering the book ****",
            type="B",
            book=self.book
        )

        self.meeting.members.add(self.user)

    def test_url(self):
        self.assertEqual(self.url, '/agenda/export')

    def test_user_exports_their_calendar(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response['Filename'], 'agenda.ics')
