"""Unit testing of the Create Vote view"""
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase, tag
from django.urls import reverse

from BookClub.models import User, ForumPost, Vote


@tag('vote', 'forum', 'post', 'createvote')
class CreateVoteViewTestCase(TestCase):
    """Tests of the Create Vote view"""
    fixtures = [
        'BookClub/tests/fixtures/default_users.json',
        'BookClub/tests/fixtures/default_posts.json',
        'BookClub/tests/fixtures/default_clubs.json',
        'BookClub/tests/fixtures/default_forum.json',
    ]

    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.post = ForumPost.objects.get(pk=1)
        self.upvoteurl = reverse('upvote')
        self.downvoteurl = reverse('downvote')
        self.forummpostcontenttypepk = ContentType.objects.get_for_model(
            self.post.__class__).pk
        self.form = {
            'content_type': self.forummpostcontenttypepk,
            'creator': 1,
            'object_id': 1,
            'type': True,
        }

    def test_upvote_url(self):
        self.assertEqual(self.upvoteurl, "/forum/upvote/")

    def test_downvote_url(self):
        self.assertEqual(self.downvoteurl, "/forum/downvote/")

    def test_json_response(self):
        self.client.login(username=self.user.username,
                          password="Password123")
        header = {'HTTP_Referer': '/forum/'}
        response = self.client.post(self.upvoteurl, self.form, **header)
        self.assertJSONEqual(response.content, {"rating": 1, "downvote": False, "upvote": True, "no_vote": False})

        self.form['type'] = False
        response = self.client.post(self.downvoteurl, self.form, **header)
        self.assertJSONEqual(response.content, {"rating": -1, "downvote": True, "upvote": False, "no_vote" : False})

    def test_valid_up_vote_none_exists(self):
        self.client.login(username=self.user.username, password="Password123")
        header = {'HTTP_Referer': '/forum/'}
        response = self.client.post(self.upvoteurl, self.form, **header)
        self.assertEqual(ForumPost.objects.get(pk=1).rating, 1)

    def test_valid_down_vote_none_exists(self):
        self.client.login(username=self.user.username, password="Password123")
        header = {'HTTP_Referer': '/forum/'}
        self.form['type'] = False
        response = self.client.post(self.upvoteurl, self.form, **header)
        self.assertEqual(ForumPost.objects.get(pk=1).rating, -1)

    def test_valid_up_vote_up_vote_exists(self):
        Vote.objects.create(
            creator=self.user,
            content_type=ContentType.objects.get(pk=self.forummpostcontenttypepk),
            object_id=self.post.pk,
            type=True
        )
        self.client.login(username=self.user.username, password="Password123")
        header = {'HTTP_Referer': '/forum/'}
        response = self.client.post(self.upvoteurl, self.form, **header)
        self.assertEqual(ForumPost.objects.get(pk=1).rating, 0)

    def test_valid_down_vote_up_vote_exists(self):
        Vote.objects.create(
            creator=self.user,
            content_type=ContentType.objects.get(
                pk=self.forummpostcontenttypepk),
            object_id=self.post.pk,
            type=True
        )
        self.client.login(username=self.user.username,
                          password="Password123")
        header = {'HTTP_Referer': '/forum/'}
        self.form['type'] = False
        response = self.client.post(self.upvoteurl, self.form, **header)
        self.assertEqual(ForumPost.objects.get(pk=1).rating, -1)

    def test_valid_up_vote_down_vote_exists(self):
        Vote.objects.create(
            creator=self.user,
            content_type=ContentType.objects.get(
                pk=self.forummpostcontenttypepk),
            object_id=self.post.pk,
            type=False
        )
        self.client.login(username=self.user.username,
                          password="Password123")
        header = {'HTTP_Referer': '/forum/'}
        response = self.client.post(self.upvoteurl, self.form, **header)
        self.assertEqual(ForumPost.objects.get(pk=1).rating, 1)

    def test_valid_down_vote_down_vote_exists(self):
        Vote.objects.create(
            creator=self.user,
            content_type=ContentType.objects.get(
                pk=self.forummpostcontenttypepk),
            object_id=self.post.pk,
            type=False
        )
        self.client.login(username=self.user.username,
                          password="Password123")
        header = {'HTTP_Referer': '/forum/'}
        self.form['type'] = False
        response = self.client.post(self.upvoteurl, self.form, **header)
        self.assertEqual(ForumPost.objects.get(pk=1).rating, 0)

    def test_invalid_form_returns_no_changes(self):
        self.client.login(username=self.user.username,
                          password="Password123")
        header = {'HTTP_Referer': '/forum/'}
        self.form.pop('creator')
        response = self.client.post(self.upvoteurl, self.form, **header)
        self.assertEqual(ForumPost.objects.get(pk=1).rating, 0)
        self.assertJSONEqual(response.content,
                             {"rating": 0, "downvote": False, "upvote": False, "no_vote": True}
                             )
    
    def test_invalid_form_object_missing(self):
        self.client.login(username=self.user.username,
                          password="Password123")
        header = {'HTTP_Referer': '/forum/'}
        self.form.pop('object_id')
        response = self.client.post(self.upvoteurl, self.form, **header, follow=False)
        self.assertEqual(ForumPost.objects.get(pk=1).rating, 0)
        self.assertRedirects(response, expected_url=reverse('global_forum'), status_code=302, target_status_code=200)
