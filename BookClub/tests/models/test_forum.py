"""Unit testing of Forum Models"""
from django.forms import ValidationError
from django.test import TestCase, tag

from BookClub.models import ForumPost, ForumComment, Forum, User, Club


@tag('models', 'forum')
class ForumTestCase(TestCase):
    """Forum Model, Fields, Validation and Methods Testing"""
    fixtures = [
        'BookClub/tests/fixtures/default_user_created_objects.json',
        'BookClub/tests/fixtures/default_users.json',
        'BookClub/tests/fixtures/default_clubs.json',
        'BookClub/tests/fixtures/default_forums_posts_and_meetings_club.json',
    ]

    def setUp(self):
        self.forum = Forum.objects.get(pk=1)
        self.forumPost = ForumPost.objects.get(pk=1)
        self.club = Club.objects.get(pk=1)
        self.user = User.objects.get(pk=1)

    def assertValid(self):
        try:
            self.forum.full_clean()
        except(ValidationError):
            self.fail('Test user created object should be valid')

    def assertInvalid(self):
        with self.assertRaises(ValidationError):
            self.forum.full_clean()

    def test_valid(self):
        self.assertValid()

    def test_associated_with_can_be_blank(self):
        self.forum.associatedWith = None
        self.assertValid()

    def test_associated_with_can_be_assigned(self):
        self.forum.associatedWith = self.club
        self.assertValid()

    def test_title_cannot_be_blank(self):
        self.forum.title = ""
        self.assertInvalid()
        self.forum.title = None
        self.assertInvalid()

    def test_title_accepts_30_chars(self):
        self.forum.title = "a" * 30
        self.assertValid()

    def test_title_rejects_31_chars(self):
        self.forum.title = "a" * 31
        self.assertInvalid()

    def test_get_posts_function(self):
        forward_set = list(ForumPost.objects.filter(forum=self.forum))
        backward_set = list(self.forum.get_posts())
        for post in forward_set:
            self.assertIn(post, backward_set)

        for post in backward_set:
            self.assertIn(post, forward_set)

    def test_get_absolute_url_global_forum(self):
        return_url = self.forum.get_absolute_url()
        correct_url = '/forum/'
        self.assertEqual(return_url, correct_url)

    def test_get_absolute_url_global_forum(self):
        return_url = self.club.forum.get_absolute_url()
        correct_url = '/club/Johnathan_Club/forum/'
        self.assertEqual(return_url, correct_url)

    def test_str_function_global_forum(self):
        return_str = str(self.forum)
        correct_str = 'Global Forum'
        self.assertEqual(return_str, correct_str)

    def test_str_function_club_forum(self):
        return_str = str(self.club.forum)
        correct_str = 'Johnathan Club Forum'
        self.assertEqual(return_str, correct_str)


@tag('models', 'post')
class ForumPostTestCase(TestCase):
    """Forum Post Model, Fields, Validation and Methods Testing"""
    fixtures = [
        'BookClub/tests/fixtures/default_user_created_objects.json',
        'BookClub/tests/fixtures/default_users.json'
    ]

    def setUp(self):
        self.forumPost = ForumPost.objects.get(pk=1)
        self.user = User.objects.get(pk=1)
        self.user2 = User.objects.get(pk=2)

    def assertValid(self):
        try:
            self.forumPost.full_clean()
        except ValidationError:
            self.fail('Test user created object should be valid')

    def assertInvalid(self):
        with self.assertRaises(ValidationError):
            self.forumPost.full_clean()

    def test_valid(self):
        self.assertValid()

    def test_votes_can_be_empty(self):
        self.forumPost.votes.clear()
        self.assertValid()

    def test_add_comment(self):
        commentsBefore = self.forumPost.get_comments().count()
        comment = ForumComment.objects.create(
            creator=self.user2,
            content="testcomment",
            post=self.forumPost
        )
        self.forumPost = ForumPost.objects.get(pk=1)
        commentsAfter = self.forumPost.get_comments().count()
        self.assertEqual(commentsBefore + 1, commentsAfter)

    def test_remove_comment(self):
        comment = ForumComment.objects.create(
            creator=self.user2,
            content="testcomment",
            post=self.forumPost
        )
        self.forumPost = ForumPost.objects.get(pk=1)
        commentsBefore = self.forumPost.get_comments().count()
        comment.delete()
        self.forumPost = ForumPost.objects.get(pk=1)
        commentsAfter = self.forumPost.get_comments().count()
        self.assertEqual(commentsBefore - 1, commentsAfter)

    def test_forum_field_is_required(self):
        self.forumPost.forum = None
        self.assertInvalid()

    def test_str_function(self):
        return_str = str(self.forumPost)
        correct_str = '"blank" post on Global Forum by johndoe'
        self.assertEqual(return_str, correct_str)

    def test_get_delete_str(self):
        return_str = self.forumPost.get_delete_str()
        correct_str = '"blank" post on Global Forum by johndoe'
        self.assertEqual(return_str, correct_str)

    def test_get_absolute_url_(self):
        return_url = self.forumPost.get_absolute_url()
        correct_url = '/forum/1/'
        self.assertEqual(return_url, correct_url)

    def test_get_delete_url(self):
        return_url = self.forumPost.get_delete_url()
        correct_url = '/forum/1/delete/'
        self.assertEqual(return_url, correct_url)


@tag('models', 'comment')
class ForumCommentTestCase(TestCase):
    """Forum Comment Model, Fields, Validation and Methods Testing"""
    fixtures = [
        'BookClub/tests/fixtures/default_user_created_objects.json',
        'BookClub/tests/fixtures/default_users.json'
    ]

    def setUp(self):
        self.forumComment = ForumComment.objects.get(pk=1)
        self.forumPost = ForumPost.objects.get(pk=1)
        self.user = User.objects.get(pk=1)
        self.user2 = User.objects.get(pk=2)

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

    def test_str_function(self):
        return_str = str(self.forumComment)
        correct_str = 'Comment by johndoe on "blank" post on Global Forum by johndoe'
        self.assertEqual(return_str, correct_str)

    def test_get_delete_str(self):
        return_str = self.forumComment.get_delete_str()
        correct_str = 'Comment by johndoe on "blank" post on Global Forum by johndoe'
        self.assertEqual(return_str, correct_str)

    def test_get_delete_url(self):
        return_url = self.forumComment.get_delete_url()
        correct_url = 'forum/1/comment/1/delete/'
