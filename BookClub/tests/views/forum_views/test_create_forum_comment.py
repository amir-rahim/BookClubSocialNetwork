from django.contrib import messages
from django.contrib.messages import get_messages
from django.test import TestCase, tag
from django.urls import reverse

from BookClub.models import User, ForumPost, Club, ForumComment
from BookClub.tests.helpers import reverse_with_next


@tag('forum', 'create_comment')
class CreateCommentViewTestCase(TestCase):
    """Tests of the Create Comments view."""

    fixtures = [
        'BookClub/tests/fixtures/default_users.json',
        'BookClub/tests/fixtures/default_clubs.json',
        'BookClub/tests/fixtures/default_memberships.json',
        'BookClub/tests/fixtures/default_forum.json',
        'BookClub/tests/fixtures/default_posts.json',
    ]

    def setUp(self):
        self.club = Club.objects.get(pk=1)
        self.user = User.objects.get(username="johndoe")
        self.global_post = ForumPost.objects.get(pk=1)
        self.url = reverse('create_forum_comment', kwargs={
            "post_id": self.global_post.pk
        })
        self.club_post = ForumPost.objects.get(pk=4)
        self.club_url = reverse('create_forum_comment',
                                kwargs={
                                    "club_url_name": self.club.club_url_name,
                                    "post_id": self.club_post.pk
                                })
        self.post = {
            "content": "HELLO, HOW DO YOU DO!",
        }

    def test_create_comment_url(self):
        self.client.login(username=self.user.username, password="Password123")
        self.assertEqual(self.url, '/forum/'+str(self.global_post.pk)+'/comment/')

    def test_create_club_comment_url(self):
        self.client.login(username=self.user.username, password="Password123")
        self.assertEqual(self.club_url, '/club/'+str(self.club.club_url_name)+'/forum/'+str(self.club_post.pk)+'/comment/')

    def test_redirect_when_not_logged_in(self):
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.post(self.url, self.post, follow=True)
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200, fetch_redirect_response=True
                             )

    def test_redirect_club_when_not_logged_in(self):
        redirect_url = reverse_with_next('login', self.club_url)
        response = self.client.post(self.club_url, self.post, follow=True)
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200, fetch_redirect_response=True
                             )

    def test_create_post_when_not_logged_in(self):
        post_count_before = ForumComment.objects.count()
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.post(self.url, self.post, follow=True)
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200, fetch_redirect_response=True
                             )
        self.assertTemplateUsed(response, 'authentication/login.html')
        post_count_after = ForumComment.objects.count()
        self.assertEqual(post_count_after, post_count_before)

    def test_create_club_comment_when_not_logged_in(self):
        post_count_before = ForumComment.objects.count()
        redirect_url = reverse_with_next('login', self.club_url)
        response = self.client.post(self.club_url, self.post, follow=True)
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200, fetch_redirect_response=True
                             )
        self.assertTemplateUsed(response, 'authentication/login.html')
        post_count_after = ForumComment.objects.count()
        self.assertEqual(post_count_after, post_count_before)

    def test_create_comment_when_logged_in(self):
        self.client.login(username=self.user.username, password="Password123")
        redirect_url = reverse('forum_post', kwargs={"post_id": self.global_post.pk})
        post_count_before = ForumComment.objects.count()
        response = self.client.post(self.url, self.post, follow=True)
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200, fetch_redirect_response=True
                             )
        post_count_after = ForumComment.objects.count()
        self.assertEqual(post_count_after, post_count_before+1)

    def test_create_club_comment_when_logged_in(self):
        self.client.login(username=self.user.username, password="Password123")
        redirect_url = reverse('forum_post', kwargs={"club_url_name": self.club.club_url_name, "post_id": self.club_post.pk})
        post_count_before = ForumComment.objects.count()
        response = self.client.post(self.club_url, self.post, follow=True)
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200, fetch_redirect_response=True
                             )
        post_count_after = ForumComment.objects.count()
        self.assertEqual(post_count_after, post_count_before+1)

    def test_create_invalid_comment(self):
        self.client.login(username=self.user.username, password="Password123")
        redirect_url = reverse('forum_post', kwargs={"post_id": self.global_post.pk})
        post_count_before = ForumComment.objects.count()
        self.post['content'] = "x" * 1025
        response = self.client.post(self.url, self.post, follow=True)
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200, fetch_redirect_response=True
                             )
        messages_list = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        self.assertEqual(str(messages_list[0]), "There was an error making that comment, try again!")
        post_count_after = ForumComment.objects.count()
        self.assertEqual(post_count_after, post_count_before)

    def test_create_invalid_post_id(self):
        self.client.login(username=self.user.username, password="Password123")
        redirect_url = reverse('forum_post', kwargs={"post_id": 1000})
        self.url = reverse('create_forum_comment', kwargs={
            "post_id": 1000
        })
        post_count_before = ForumComment.objects.count()
        response = self.client.post(self.url, self.post, follow=True)
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=404, fetch_redirect_response=True
                             )
        messages_list = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        self.assertEqual(str(messages_list[0]), "There was an error making that comment, try again!")
        post_count_after = ForumComment.objects.count()
        self.assertEqual(post_count_after, post_count_before)