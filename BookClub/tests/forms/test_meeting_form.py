from django import forms
from django.test import TestCase, tag
from BookClub.models import User, Club, ClubMembership, Meeting, Book
from BookClub.forms.meeting import MeetingForm

from datetime import date, datetime
@tag('meetingform','meeting')
class MeetingFormTestCase(TestCase):
    """Unit tests for Meeting Form"""

    fixtures = [
        "BookClub/tests/fixtures/default_users.json",
        "BookClub/tests/fixtures/default_clubs.json",
        "BookClub/tests/fixtures/default_books.json",
    ]

    def setUp(self):

        self.user = User.objects.get(pk=1)
        self.book = Book.objects.get(pk=1)
        self.club = Club.objects.get(pk=3)

        self.form_input = {
            "title": "Weekly book review",
            "description": "This is our first weekly meeting for this weeks book!",
            "meeting_time": "2022-02-26 15:30:00",
            "location": "Maughan Library",
            "type": "B",
            "book": self.book.id,
        }

    def test_valid_meeting_form(self):
        form = MeetingForm(data = self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_has_necessary_fields(self):
        form = MeetingForm()
        self.assertIn('title', form.fields)
        self.assertIn('description', form.fields)
        self.assertIn('meeting_time', form.fields)
        self.assertIn('location', form.fields)
        self.assertIn('type', form.fields)
        self.assertIn('book', form.fields)
        self.assertNotIn('organiser', form.fields)
        self.assertNotIn('club', form.fields)
        self.assertNotIn('members', form.fields)
        self.assertNotIn('created_on', form.fields)

    def test_form_must_save_correctly(self):
        form = MeetingForm(data = self.form_input)
        before_count = Meeting.objects.count()
        saving_date = date.today()
        meeting = form.save(commit=False)
        meeting.organiser = self.user
        meeting.club = self.club
        meeting.save()
        after_count = Meeting.objects.count()
        self.assertEqual(after_count, before_count + 1)
        meeting = Meeting.objects.get(title = self.form_input['title'])
        self.assertEqual(meeting.title, self.form_input['title'])
        self.assertEqual(meeting.description, self.form_input['description'])
        # self.assertEqual(meeting.meeting_time, datetime.strptime(self.form_input['meeting_time'], '%Y-%m-%d %H:%M:%S'))
        self.assertEqual(meeting.location, self.form_input['location'])
        self.assertEqual(meeting.type, self.form_input['type'])
        self.assertEqual(meeting.book.id, self.form_input['book'])
        self.assertEqual(meeting.organiser, self.user)
        self.assertEqual(meeting.club, self.club)
        self.assertEqual(meeting.created_on, saving_date)
