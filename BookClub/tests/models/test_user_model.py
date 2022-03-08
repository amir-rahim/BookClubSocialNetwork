from django.test import TestCase, tag
from BookClub.models import User, BookReview
from django.core.exceptions import ValidationError  # Create your tests here.

@tag('usermodel','user')
class UserModelTestCase(TestCase):

    fixtures = ['BookClub/tests/fixtures/default_users.json']

    def setUp(self):
        self.user = User.objects.get(username='johndoe')

    def test_valid_user(self):
        self._assert_user_is_valid()

    def _assert_user_is_valid(self):
        try:
            self.user.full_clean()
        except (ValidationError):
            self.fail('Test user should be valid')

    def _assert_user_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.user.full_clean()

    def test_username_cannot_be_blank(self):
        self.user.username = ''
        self._assert_user_is_invalid()

    def test_username_can_be_30chars(self):
        self.user.username = 'a' + 'x' * 29
        self._assert_user_is_valid()

    def test_username_cannot_be_greater_than_30_chars(self):
        self.user.username = 'a' + 'x' * 30
        self._assert_user_is_invalid()

    def test_username_may_contain_numbers(self):
        self.user.username = 'johndo1e'
        self._assert_user_is_valid()

    def test_bio_can_take_250_char(self):
        self.user.bio = '@' + 'x' * 248
        self._assert_user_is_valid()

    def test_bio_cannot_take_251_char(self):
        self.user.public_bio = '@' + 'x' * 250
        self._assert_user_is_invalid()

    def test_bio_cannot_be_blank(self):
        self.user.public_bio = ""
        self._assert_user_is_invalid()

    def test_gravatar_correct_return(self):
        gravatar = "https://www.gravatar.com/avatar/fd876f8cd6a58277fc664d47ea10ad19?size=120&default=mp"
        self.assertEqual(gravatar, self.user.gravatar())
