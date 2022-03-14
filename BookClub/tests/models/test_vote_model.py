from django.contrib.contenttypes.models import ContentType
from django.db import IntegrityError
from django.forms import ValidationError
from django.test import TestCase, tag

from BookClub.models import Vote, ForumPost, ForumComment, User


@tag('models', 'vote')
class VoteModelTestCase(TestCase):
    fixtures = [
        'BookClub/tests/fixtures/default_users.json',
        'BookClub/tests/fixtures/default_votes.json',
        'BookClub/tests/fixtures/default_user_created_objects',
    ]

    def setUp(self):
        self.vote = Vote.objects.get(pk=1)
        self.forum_post = ForumPost.objects.get(pk=1)
        self.user = User.objects.get(pk=1)
        self.forum_post.add_vote(self.vote)
        self.user2 = User.objects.get(pk=2)
        self.forum_post.update_rating()
        self.forum_comment = ForumComment.objects.get(pk=1)

    def assertValid(self):
        try:
            self.vote.full_clean()
        except ValidationError:
            self.fail('Test user created object should be valid')

    def assertInvalid(self):
        with self.assertRaises(ValidationError):
            self.vote.full_clean()

    def test_vote_is_valid(self):
        self.assertValid()

    def test_type_cannot_be_null_or_blank(self):
        self.vote.type = None
        self.assertInvalid()
        self.vote.type = ""
        self.assertInvalid()

    def test_content_type_cannot_be_null_or_blank(self):
        self.vote.content_type = None
        self.assertInvalid()

    def test_target_must_be_defined(self):
        self.vote.target = None
        self.assertInvalid()

    def test_unique_creator_target_only(self):
        with self.assertRaises(IntegrityError):
            vote2 = Vote.objects.create(
                creator=self.user,
                created_on="2022-02-27T22:45:06.275Z",
                type=True,
                content_type=ContentType.objects.get_for_model(self.forum_post),
                object_id=1
            )

    def test_save_correctly_adds_vote_and_updates_rating_for_content_up_vote(self):
        ratingBefore = self.forum_post.get_rating()
        vote2 = Vote.objects.create(
            creator=self.user2,
            created_on="2022-02-27T22:45:06.275Z",
            type=True,
            content_type=ContentType.objects.get_for_model(self.forum_post),
            object_id=1
        )
        self.forum_post = ForumPost.objects.get(pk=1)
        self.forum_post.update_rating()
        ratingAfter = self.forum_post.get_rating()
        self.assertLess(ratingBefore, ratingAfter)

    def test_save_correctly_adds_vote_and_updates_rating_for_content_down_vote(self):
        ratingBefore = self.forum_post.get_rating()
        vote2 = Vote.objects.create(
            creator=self.user2,
            created_on="2022-02-27T22:45:06.275Z",
            type=False,
            content_type=ContentType.objects.get_for_model(self.forum_post),
            object_id=1
        )
        self.forum_post = ForumPost.objects.get(pk=1)
        ratingAfter = self.forum_post.get_rating()
        self.assertGreater(ratingBefore, ratingAfter)

    def test_save_target_does_not_exist(self):
        self.forum_post.delete()
        with self.assertRaises(Exception):
            vote2 = Vote.objects.create(
                creator=self.user2,
                created_on="2022-02-27T22:45:06.275Z",
                type=False,
                content_type=ContentType.objects.get_for_model(self.forum_post),
                object_id=1
            )

    def test_remove_upvote(self):
        self.vote2 = Vote.objects.create(
            creator=self.user2,
            created_on="2022-02-27T22:45:06.275Z",
            type=True,
            content_type=ContentType.objects.get_for_model(self.forum_post),
            object_id=1
        )
        self.forum_post.add_vote(self.vote2)
        ratingBefore = self.forum_post.get_rating()
        self.vote2.delete()
        self.forum_post = ForumPost.objects.get(pk=1)
        ratingAfter = self.forum_post.get_rating()
        self.assertLess(ratingAfter, ratingBefore)

    def test_delete_target_exists(self):
        ratingBefore = self.forum_post.get_rating()
        votesBefore = self.forum_post.votes.all().count()
        self.vote.delete()
        self.forum_post = ForumPost.objects.get(pk=1)
        ratingAfter = self.forum_post.get_rating()
        votesAfter = self.forum_post.votes.all().count()
        self.assertGreater(ratingAfter, ratingBefore)
        self.assertGreater(votesBefore, votesAfter)

    def test_delete_target_does_not_exist(self):
        self.forum_post.delete()
        self.vote.delete()

    def test_content_type(self):
        self.assertEqual(self.forum_post.get_content_type(), ForumPost)
        self.assertEqual(self.forum_comment.get_content_type(), ForumComment)

