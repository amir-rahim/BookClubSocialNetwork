from django.test import TestCase

from BookClub.models.club import Club
from django.core.exceptions import ValidationError

class ClubModelTestCase(TestCase):

    fixtures = ['BookClub/tests/fixtures/default_clubs.json']

    def setUp(self):
        self.club1 = Club.objects.get(pk = 1)
        self.club2 = Club.objects.get(pk = 2)

    def _assert_club_is_valid(self):
        try:
            self.club1.full_clean()
        except(ValidationError):
            self.fail('Test club should be valid')

    def _assert_club_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.club1.full_clean()

    def test_valid_club(self):
        self._assert_club_is_valid()


# Name testing
    def test_name_cannot_be_blank(self):
        self.club1.name = ''
        self._assert_club_is_invalid()

    def test_name_may_already_exist(self):
        self.club1.name = self.club2.name
        self._assert_club_is_valid()

    def test_name_can_be_100_characters_long(self):
        self.club1.name = 'x' * 100
        self._assert_club_is_valid()

    def test_name_cannot_be_over_100_characters_long(self):
        self.club1.name = 'x' * 101
        self._assert_club_is_invalid()

# Description testing
    def test_description_cannot_be_blank(self):
        self.club1.description = ''
        self._assert_club_is_invalid()

    def test_description_can_be_200_characters_long(self):
        self.club1.description = 'x' * 200
        self._assert_club_is_valid()

    def test_description_cannot_be_over_200_characters_long(self):
        self.club1.description = 'x' * 201
        self._assert_club_is_invalid()

# Rules testing
    def test_rules_can_be_blank(self):
        self.club1.rules = ''
        self._assert_club_is_valid()

    def test_rules_can_be_200_characters_long(self):
        self.club1.rules = 'x' * 200
        self._assert_club_is_valid()

    def test_rules_cannot_be_over_200_characters_long(self):
        self.club1.description = 'x' * 201
        self._assert_club_is_invalid()

# Privacy testing
    def test_privacy_cannot_be_empty(self):
        self.club1.is_private = None
        self._assert_club_is_invalid()

    def test_club_can_be_private(self):
        self.club1.is_private = True
        self._assert_club_is_valid()

    def test_club_can_be_private(self):
        self.club1.is_private = False
        self._assert_club_is_valid()
