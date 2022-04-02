"""Unit testing for the Voting Tags"""
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase, tag

from BookClub.models import User, ForumPost, Vote
from BookClub.templatetags.votingtags import has_user_voted, get_user_vote_type


@tag('tags', 'vote')
class HasUserVotedTagTestCase(TestCase):
    """Tests of the HasUserVoted tag"""
    fixtures = [
        'BookClub/tests/fixtures/default_clubs.json',
        'BookClub/tests/fixtures/default_forum.json',
        'BookClub/tests/fixtures/default_users.json',
        'BookClub/tests/fixtures/default_posts.json',
    ]

    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.post = ForumPost.objects.get(pk=1)
        self.forum_post_content_type_pk = ContentType.objects.get_for_model(
            self.post.__class__).pk

    def test_user_has_voted_has_not_voted(self):
        self.votes = self.post.votes.all()
        self.assertFalse(has_user_voted(None, self.votes, self.user))

    def test_user_has_voted_has_down_voted(self):
        Vote.objects.create(
            creator=self.user,
            content_type=ContentType.objects.get(
                pk=self.forum_post_content_type_pk),
            object_id=self.post.pk,
            type=False
        )
        self.votes = self.post.votes.all()
        self.assertTrue(has_user_voted(None, self.votes, self.user))

    def test_user_has_voted_has_up_voted(self):
        Vote.objects.create(
            creator=self.user,
            content_type=ContentType.objects.get(
                pk=self.forum_post_content_type_pk),
            object_id=self.post.pk,
            type=True
        )
        self.votes = self.post.votes.all()
        self.assertTrue(has_user_voted(None, self.votes, self.user))


@tag('tags', 'vote')
class GetUserVoteTagTestCase(TestCase):
    """Tests of the GetUserVote tag"""
    fixtures = [
        'BookClub/tests/fixtures/default_clubs.json',
        'BookClub/tests/fixtures/default_forum.json',
        'BookClub/tests/fixtures/default_users.json',
        'BookClub/tests/fixtures/default_posts.json',
    ]

    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.post = ForumPost.objects.get(pk=1)
        self.forum_post_content_type_pk = ContentType.objects.get_for_model(
            self.post.__class__).pk

    def test_get_vote_has_not_voted(self):
        self.votes = self.post.votes.all()
        self.assertIsNone(get_user_vote_type(None, self.votes, self.user))

    def test_get_vote_has_upvoted(self):
        vote = Vote.objects.create(
            creator=self.user,
            content_type=ContentType.objects.get(
                pk=self.forum_post_content_type_pk),
            object_id=self.post.pk,
            type=True
        )
        self.votes = self.post.votes.all()
        self.assertEqual(get_user_vote_type(None, self.votes, self.user), vote.type)

    def test_get_vote_has_downvoted(self):
        vote = Vote.objects.create(
            creator=self.user,
            content_type=ContentType.objects.get(
                pk=self.forum_post_content_type_pk),
            object_id=self.post.pk,
            type=False
        )
        self.votes = self.post.votes.all()
        self.assertEqual(get_user_vote_type(
            None, self.votes, self.user), vote.type)
