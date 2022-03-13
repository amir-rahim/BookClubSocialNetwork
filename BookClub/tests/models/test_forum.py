from django.forms import ValidationError
from django.test import TestCase, tag

from BookClub.models import ForumPost, ForumComment, Forum, User, Club


@tag('models', 'post')
class ForumPostTestCase(TestCase):
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

    def test_comments_can_be_empty(self):
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
        self.assertLess(commentsBefore, commentsAfter)

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
        self.assertGreater(commentsBefore, commentsAfter)


@tag('models', 'comment')
class ForumCommentTestCase(TestCase):
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


@tag('models', 'forum')
class ForumTestCase(TestCase):
    fixtures = [
        'BookClub/tests/fixtures/default_user_created_objects.json',
        'BookClub/tests/fixtures/default_users.json',
        'BookClub/tests/fixtures/default_clubs.json'
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

    def test_posts_can_be_blank(self):
        self.forum.posts.clear()
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

    def test_add_comment(self):
        postsBefore = self.forum.posts.all().count()
        self.forum.add_post(self.forumPost)
        self.forum = Forum.objects.get(pk=1)
        postsAfter = self.forum.posts.all().count()
        self.assertLess(postsBefore, postsAfter)

    def test_remove_comment(self):
        self.forum.add_post(self.forumPost)
        self.forum = Forum.objects.get(pk=1)
        postsBefore = self.forum.posts.all().count()
        self.forum.remove_post(self.forumPost)
        self.forum = Forum.objects.get(pk=1)
        postsAfter = self.forum.posts.all().count()
        self.assertGreater(postsBefore, postsAfter)
