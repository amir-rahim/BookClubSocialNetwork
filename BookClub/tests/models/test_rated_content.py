"""Unit testing of Rated Content Models"""
from django.forms import ValidationError
from django.test import TestCase, tag

from BookClub.models import ForumPost, ForumComment, User


@tag('models', 'textpost')
class TextPostTestCase(TestCase):
    """Text Post Model, Fields, Validation and Methods Testing"""
    fixtures = [
        'BookClub/tests/fixtures/default_user_created_objects.json',
        'BookClub/tests/fixtures/default_users.json'
    ]

    def setUp(self):
        self.forumPost = ForumPost.objects.get(pk=1)
        self.user = User.objects.get(pk=1)

    def assertValid(self):
        try:
            self.forumPost.full_clean()
        except ValidationError:
            self.fail('Test user created object should be valid')

    def assertInvalid(self):
        with self.assertRaises(ValidationError):
            self.forumPost.full_clean()

    def test_valid_forumPost(self):
        self.assertValid()

    def test_content_accepts_1024_char(self):
        self.forumPost.content = ("a" * 1024)
        self.assertValid()

    def test_content_rejects_above_1024_chars(self):
        self.forumPost.content = "a" + ("a" * 1024)
        self.assertInvalid()

    def test_content_cannot_be_blank(self):
        self.forumPost.content = ""
        self.assertInvalid()

    def test_title_cannot_be_blank(self):
        self.forumPost.title = ""
        self.assertInvalid()

    def test_title_accepts_30_chars(self):
        self.forumPost.title = ("a" * 30)
        self.assertValid()

    def test_title_rejects_31_chars(self):
        self.forumPost.title = ("a" * 31)
        self.assertInvalid()


@tag('models', 'comment')
class TextCommentTestCase(TestCase):
    """Text Comment Model, Fields, Validation and Methods Testing"""
    fixtures = [
        'BookClub/tests/fixtures/default_user_created_objects.json',
        'BookClub/tests/fixtures/default_users.json'
    ]

    def setUp(self):
        self.forumComment = ForumComment.objects.get(pk=1)
        self.user = User.objects.get(pk=1)

    def assertValid(self):
        try:
            self.forumComment.full_clean()
        except(ValidationError):
            self.fail('Test user created object should be valid')

    def assertInvalid(self):
        with self.assertRaises(ValidationError):
            self.forumComment.full_clean()

    def test_valid(self):
        self.assertValid()

    def test_content_accepts_240_chars(self):
        self.forumComment.content = ("a" * 240)
        self.assertValid()

    def test_content_rejects_241_chars(self):
        self.forumComment.content = ("a" * 241)
        self.assertInvalid()

    def test_content_rejects_blank_chars(self):
        self.forumComment.content = ""
        self.assertInvalid()
