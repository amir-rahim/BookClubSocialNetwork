from ast import Pass
from django.test import TestCase
from django.utils import timezone
import pytz
import datetime

from BookClub.models import Meeting, Club, User, Book
# from BookClub.models.club_membership import ClubMembership
from django.core.exceptions import ValidationError

class MeetingTestCase(TestCase):

    fixtures = [
        'BookClub/tests/fixtures/books.json',
        'BookClub/tests/fixtures/default_users.json',
        'BookClub/tests/fixtures/default_clubs.json',
        'BookClub/tests/fixtures/default_meetings.json'
    ]

    def setUp(self):
        self.club = Club.objects.get(pk = 1)
        self.meeting = Meeting.objects.get(pk = 1)
        self.user = User.objects.get(username = 'johndoe')
        self.jack = User.objects.get(username = "jackdoe")
        self.jane = User.objects.get(username = 'janedoe')
        self.book = Book.objects.get(pk = 1)
    
    def _assert_meeting_is_valid(self):
        try:
            self.meeting.full_clean()
        except(ValidationError):
            self.fail('test meeting should be valid')
        
    def _assert_meeting_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.meeting.full_clean()

    def test_valid_club(self):
        self._assert_meeting_is_valid()

# Field testing

    # Organiser testing

    def test_organiser_cannot_be_blank(self):
        self.meeting.organiser = None
        self._assert_meeting_is_invalid()

    # Club testing

    def test_club_cannot_be_blank(self):
        self.meeting.club = None
        self._assert_meeting_is_invalid()

    # Meeting time testing

    def test_meeting_time_cannot_be_blank(self):
        self.meeting.meeting_time = ''
        self._assert_meeting_is_invalid()

    # Location testing

    def test_location_can_be_120_long(self):
        self.meeting.location = 'x' * 120
        self._assert_meeting_is_valid()

    def test_location_cannot_be_over_120_long(self):
        self.meeting.location = 'x' * 121
        self._assert_meeting_is_invalid()

    def test_location_can_be_blank(self):
        self.meeting.location = ''
        self._assert_meeting_is_valid()

    # Title testing

    def test_title_can_be_120_long(self):
        self.meeting.title = 'x' * 120
        self._assert_meeting_is_valid()

    def test_title_cannot_be_over_120_long(self):
        self.meeting.title = 'x' * 121
        self._assert_meeting_is_invalid()

    def test_title_cannot_be_blank(self):
        self.meeting.title = ''
        self._assert_meeting_is_invalid()

    # Description testing

    def test_description_can_be_250_long(self):
        self.meeting.description = 'x' * 250
        self._assert_meeting_is_valid()

    def test_description_cannot_be_over_250_long(self):
        self.meeting.description = 'x' * 251
        self._assert_meeting_is_invalid()

    def test_description_cannot_be_blank(self):
        self.meeting.description = ''
        self._assert_meeting_is_invalid()

    # Members testing

    def test_member_can_join(self):
        self.meeting.join_member(self.jack)
        self.assertEquals(self.meeting.get_members().count(), 3)
        self._assert_meeting_is_valid()

    def test_member_can_leave(self):
        self.meeting.leave_member(self.user)
        self.assertEquals(self.meeting.get_members().count(), 1)
        self._assert_meeting_is_valid()


    # Type testing

    def test_meeting_type_enum_is_invalid(self):
        self.meeting.type = 'x'
        self._assert_meeting_is_invalid()

    def test_meeting_type_enum_is_valid(self):
        self.meeting.type = 'B'
        self._assert_meeting_is_valid()

    # Book testing

    def test_book_can_be_blank(self):
        self.meeting.book = None
        self._assert_meeting_is_valid()
        
# Function testing
    def test_str_returns_title(self):
        self.assertEqual(str(self.meeting), self.meeting.get_title())

    def test_get_organiser(self):
        self.assertEqual(self.meeting.get_organiser(), self.user)

    def test_get_club(self):
        self.assertEqual(self.meeting.get_club(), self.club)

    def test_get_meeting_time(self):
        self.assertEqual(str(self.meeting.get_meeting_time()), "2022-02-22 19:00:00+00:00")

    def test_get_created_on(self):
        self.assertEqual(self.meeting.get_created_on(), datetime.date(2022, 2, 10))

    def test_get_location(self):
        self.assertEqual(self.meeting.get_location(), "Franklin Wilkins Library GS04")
    
    def test_get_title(self):
        self.assertEqual(self.meeting.get_title(), "Book meeting 1")

    def test_get_description(self):
        self.assertEqual(self.meeting.get_description(), "This is a book meeting, helll yeahhhh")
    
    def test_get_members(self):
        self.assertQuerysetEqual(self.meeting.get_members(), [self.user, self.jane], ordered = False)

    def test_get_type(self):
        self.assertEqual(self.meeting.get_type(), "B")

    def test_get_book(self):
        self.assertEqual(self.meeting.get_book(), self.book)
    
    def test_get_number_of_attendants(self):
        self.assertEqual(self.meeting.get_number_of_attendants(), 2)

    def test_not_join_member(self):
        self.meeting.join_member(self.user)
        self.assertNotEqual(self.meeting.get_number_of_attendants(), 3)
    
    def test_not_leave_member(self):
        self.meeting.leave_member(self.jack)
        self.assertNotEqual(self.meeting.get_number_of_attendants(), 1)
    
    def test_get_is_past(self):
        self.assertEqual(self.meeting.get_is_past(), True)