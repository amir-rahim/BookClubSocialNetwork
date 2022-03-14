from django.test import TestCase, tag
from BookClub.models import User, ForumPost, Vote
from BookClub.templatetags.votingtags import has_user_voted, get_user_vote_type
from django.contrib.contenttypes.models import ContentType

@tag('vote','post','tag')
class HasUserVotedTagTestCase(TestCase):
    fixtures = [
        
        'BookClub/tests/fixtures/default_users.json',
        'BookClub/tests/fixtures/default_posts.json',
    ]
    #test cases
    #test user has voted, has not voted
    #test user has voted, has voted
    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.post = ForumPost.objects.get(pk=1)
        self.forummpostcontenttypepk = ContentType.objects.get_for_model(
            self.post.__class__).pk

    def test_user_has_voted_has_not_voted(self):
        self.assertFalse(has_user_voted(None, self.post, self.user))
        
    def test_user_has_voted_has_down_voted(self):
        Vote.objects.create(
            creator=self.user,
            content_type=ContentType.objects.get(
                pk=self.forummpostcontenttypepk),
            object_id=self.post.pk,
            type=False
        )
        self.assertTrue(has_user_voted(None, self.post, self.user))
        
    def test_user_has_voted_has_up_voted(self):
        Vote.objects.create(
            creator=self.user,
            content_type=ContentType.objects.get(
                pk=self.forummpostcontenttypepk),
            object_id=self.post.pk,
            type=True
        )
        self.assertTrue(has_user_voted(None, self.post, self.user))
        
@tag('tag')
class GetUserVoteTagTestCase(TestCase):
    fixtures = [

        'BookClub/tests/fixtures/default_users.json',
        'BookClub/tests/fixtures/default_posts.json',
    ]
    #test cases
    #test get vote, upvoted
    #test get vote, downvoted

    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.post = ForumPost.objects.get(pk=1)
        self.forummpostcontenttypepk = ContentType.objects.get_for_model(
            self.post.__class__).pk
        
    def test_get_vote_has_not_voted(self):
        self.assertIsNone(get_user_vote_type(None,self.post, self.user))

    def test_get_vote_has_upvoted(self):
        vote = Vote.objects.create(
            creator=self.user,
            content_type=ContentType.objects.get(
                pk=self.forummpostcontenttypepk),
            object_id=self.post.pk,
            type=True
        )
        self.assertEqual(get_user_vote_type(None, self.post, self.user), vote.type)
        
    def test_get_vote_has_downvoted(self):
        vote = Vote.objects.create(
            creator=self.user,
            content_type=ContentType.objects.get(
                pk=self.forummpostcontenttypepk),
            object_id=self.post.pk,
            type=False
        )
        self.assertEqual(get_user_vote_type(
            None, self.post, self.user), vote.type)

