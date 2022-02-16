from django.test import TestCase, tag

from BookClub.models.club import Club, ClubMembership
# from BookClub.models.club_membership import ClubMembership
from django.core.exceptions import ValidationError
@tag('clubmodel', 'club')
class ClubModelTestCase(TestCase):

    fixtures = [
        'BookClub/tests/fixtures/default_users.json',
        'BookClub/tests/fixtures/default_clubs.json',
        'BookClub/tests/fixtures/default_club_owners.json',
        ]

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

    def test_name_must_be_unique(self):
        self.club1.name = self.club2.name
        self._assert_club_is_invalid()

    def test_name_can_be_100_characters_long(self):
        self.club1.name = 'x' * 100
        self._assert_club_is_valid()

    def test_name_cannot_be_over_100_characters_long(self):
        self.club1.name = 'x' * 101
        self._assert_club_is_invalid()
        
#URL Name Testing
    def test_url_name_cannot_be_blank(self):
        self.club1.url_name = ''
        self._assert_club_is_invalid()

    def test_url_name_must_be_unique(self):
        self.club1.url_name = self.club2.url_name
        self._assert_club_is_invalid()
        
    def test_url_name_can_be_100_characters_long(self):
        self.club1.url_name = 'x' * 100
        self._assert_club_is_valid()

    def test_url_name_cannot_be_over_100_characters_long(self):
        self.club1.url_name = 'x' * 101
        self._assert_club_is_invalid()
        
    def test_url_name_cannot_have_special_chars(self):
        self.club1.url_name = 'x/xaaa'
        self._assert_club_is_invalid()
        
    def test_url_name_can_have_underscores(self):
        self.club1.url_name = 'x_xaaa'
        self._assert_club_is_valid()

# Description testing
    def test_description_cannot_be_blank(self):
        self.club1.description = ''
        self._assert_club_is_invalid()

    def test_description_can_be_250_characters_long(self):
        self.club1.description = 'x' * 250
        self._assert_club_is_valid()

    def test_description_cannot_be_over_250_characters_long(self):
        self.club1.description = 'x' * 251
        self._assert_club_is_invalid()

# Tagline testing
    def test_tagline_can_be_blank(self):
        self.club1.tagline = ''
        self._assert_club_is_valid()

    def test_tagline_can_be_120_characters_long(self):
        self.club1.tagline = 'x' * 120
        self._assert_club_is_valid()

    def test_tagline_cannot_be_over_120_characters_long(self):
        self.club1.tagline = 'x' * 121
        self._assert_club_is_invalid()

# Rules testing
    def test_rules_can_be_blank(self):
        self.club1.rules = ''
        self._assert_club_is_valid()

    def test_rules_can_be_200_characters_long(self):
        self.club1.rules = 'x' * 200
        self._assert_club_is_valid()

    def test_rules_cannot_be_over_200_characters_long(self):
        self.club1.rules = 'x' * 201
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

# Getters testing
    def test_get_number_of_members(self):
        owner1 = ClubMembership.objects.get(club = self.club1, membership = ClubMembership.UserRoles.OWNER)
        self.assertEqual(self.club1.get_club_owner(), owner1, 'Club object returned a wrong owner')

    def test_get_number_of_members(self):
        number_of_members = ClubMembership.objects.filter(club = self.club1, membership__gte = ClubMembership.UserRoles.MEMBER).count()
        self.assertEqual(self.club1.get_number_of_members(), number_of_members, 'Club object returned a wrong number of members')
        
    def test_convert_to_url_replaces_spaces(self):
        testName = "Daves Club Of Spaces"
        expectedUrl = "Daves_Club_Of_Spaces"
        resultUrl = Club.convertNameToUrl(None, testName)
        self.assertEqual(expectedUrl, resultUrl)
        
    def test_convert_to_url_replaces_non_alpha_numerics(self):
        testName = "Dave's?ClubOfSpaces!"
        expectedUrl = "DavesClubOfSpaces"
        resultUrl = Club.convertNameToUrl(None, testName)
        self.assertEqual(expectedUrl, resultUrl)
    
    def test_convert_to_url_replaces_non_alpha_numerics_and_spaces(self):
        testName = "Dave's ?Club Of Spaces!"
        expectedUrl = "Daves_Club_Of_Spaces"
        resultUrl = Club.convertNameToUrl(None, testName)
        self.assertEqual(expectedUrl, resultUrl)
    
