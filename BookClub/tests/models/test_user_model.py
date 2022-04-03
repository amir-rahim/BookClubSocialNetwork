"""Unit testing for User Model"""
from django.core.exceptions import ValidationError
from django.test import TestCase, tag

from BookClub.models import User, BookList


@tag('models', 'user')
class UserModelTestCase(TestCase):
    """User Model, Fields, Validation and Methods Testing"""
    fixtures = [
        'BookClub/tests/fixtures/default_books.json',
        'BookClub/tests/fixtures/default_users.json',
        'BookClub/tests/fixtures/booklists.json'
    ]
    

    def setUp(self):
        self.user = User.objects.get(username='johndoe')
        self.booklist = BookList.objects.get(pk=1)

    def test_valid_user(self):
        self._assert_user_is_valid()

    def _assert_user_is_valid(self):
        try:
            self.user.full_clean()
        except ValidationError:
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

    def test_str_function(self):
        return_str = str(self.user)
        correct_str = f'johndoe'
        self.assertEqual(return_str, correct_str)

    def test_get_absolute_url(self):
        return_url = self.user.get_absolute_url()
        correct_url = '/profile/johndoe/'
        self.assertEqual(return_url, correct_url)

    def test_save_booklist_works_correctly(self):
        self.user.save_booklist(self.booklist)
        self.assertTrue(self.user.saved_booklists.all().filter(pk=self.booklist.id))

    def test_save_booklist_does_not_save_same_book_twice(self):
        self.user.save_booklist(self.booklist)
        before_count = self.user.saved_booklists.all().count()
        self.user.save_booklist(self.booklist)
        after_count = self.user.saved_booklists.all().count()
        self.assertEqual(before_count, after_count)

    def test_get_saved_booklists(self):
        self.user.saved_booklists.add(self.booklist)
        self.assertQuerysetEqual(self.user.saved_booklists.all(),self.user.get_saved_booklists())

    def test_remove_from_saved_booklists_works_correctly(self):
        self.user.save_booklist(self.booklist)
        self.user.remove_from_saved_booklists(self.booklist)
        self.assertFalse(self.user.saved_booklists.all().filter(pk=self.booklist.id))
