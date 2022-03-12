from django.test import TestCase, tag
from BookClub.models import Poll, Club
from django.core.exceptions import ValidationError

"""Test case for Poll model"""
@tag('poll', 'models')
class PollModelTestCase(TestCase):

    fixtures = [
        'BookClub/tests/fixtures/default_clubs.json',
        'BookClub/tests/fixtures/default_polls.json',
    ]

    def setUp(self):
        self.poll = Poll.objects.get(pk=1)

    def _assert_poll_is_valid(self):
        try:
            self.poll.full_clean()
        except(ValidationError):
            self.fail('Test poll should be valid')

    def _assert_poll_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.poll.full_clean()


# Fields testing

    # Tests of title attribute

    def test_title_cannot_be_blank(self):
        self.poll.title = ""
        self._assert_poll_is_invalid()

    def test_title_can_be_between_1_and_120_characters_long(self):
        self.poll.title = 'x' * 1
        self._assert_poll_is_valid()
        self.poll.title = 'x' * 120
        self._assert_poll_is_valid()

    def test_title_cannot_be_more_than_120_characters_long(self):
        self.poll.title = 'x' * 121
        self._assert_poll_is_invalid()

    # Tests of active attribute

    def test_active_cannot_be_null(self):
        self.poll.active = None
        self._assert_poll_is_invalid()

    def test_active_is_true_by_default(self):
        poll2 = Poll.objects.create(title="Test poll 2", club=Club.objects.get(pk=1))
        self.assertEqual(poll2.active, True)

    def test_active_can_be_false(self):
        self.poll.active = False
        self._assert_poll_is_valid()

    # Tests of deadline attribute

    def test_deadline_can_be_blank(self):
        self.poll.deadline = None
        self._assert_poll_is_valid()
        self.poll.deadline = ""
        self._assert_poll_is_valid()
