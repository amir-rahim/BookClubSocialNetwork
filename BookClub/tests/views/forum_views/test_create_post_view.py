"""Unit testing of the Create Posts views"""
from django.contrib import messages
from django.contrib.messages import get_messages
from django.test import TestCase, tag
from django.urls import reverse

from BookClub.models import User, ForumPost, Club, Forum
from BookClub.tests.helpers import reverse_with_next


@tag('views', 'forum', 'create_post')
class CreatePostViewTestCase(TestCase):
    """Tests of the Create Posts view."""

    fixtures = [
        'BookClub/tests/fixtures/default_users.json',
        'BookClub/tests/fixtures/default_clubs.json',
        'BookClub/tests/fixtures/default_memberships.json',
        'BookClub/tests/fixtures/default_empty_forum.json',
    ]

    def setUp(self):
        self.url = reverse('create_forum_post')
        self.club = Club.objects.get(pk=1)
        self.club_url = reverse('create_forum_post', kwargs={"club_url_name": self.club.club_url_name})
        self.user = User.objects.get(username="johndoe")
        self.global_forum = Forum.objects.get(pk=1)
        self.club_forum = Forum.objects.get(pk=2)
        self.post = {
            "title": "Lorem Ipsum",
            "content": "HELLO, HOW DO YOU DO!",
        }

    def test_create_post_url(self):
        self.client.login(username=self.user.username, password="Password123")
        self.assertEqual(self.url, '/forum/post/')

    def test_create_club_post_url(self):
        self.client.login(username=self.user.username, password="Password123")
        self.assertEqual(self.club_url, '/club/'+self.club.club_url_name+'/forum/post/')

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
        post_count_before = ForumPost.objects.count()
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.post(self.url, self.post, follow=True)
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200, fetch_redirect_response=True
                             )
        self.assertTemplateUsed(response, 'authentication/login.html')
        post_count_after = ForumPost.objects.count()
        self.assertEqual(post_count_after, post_count_before)

    def test_create_club_post_when_not_logged_in(self):
        post_count_before = ForumPost.objects.count()
        redirect_url = reverse_with_next('login', self.club_url)
        response = self.client.post(self.club_url, self.post, follow=True)
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200, fetch_redirect_response=True
                             )
        self.assertTemplateUsed(response, 'authentication/login.html')
        post_count_after = ForumPost.objects.count()
        self.assertEqual(post_count_after, post_count_before)

    def test_create_post_when_logged_in(self):
        self.client.login(username=self.user.username, password="Password123")
        redirect_url = reverse('global_forum')
        post_count_before = ForumPost.objects.count()
        self.post['forum'] = self.global_forum
        response = self.client.post(self.url, self.post, follow=True)
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200, fetch_redirect_response=True
                             )
        post_count_after = ForumPost.objects.count()
        self.assertEqual(post_count_after, post_count_before+1)

    def test_create_club_post_when_logged_in(self):
        self.client.login(username=self.user.username, password="Password123")
        redirect_url = reverse('club_forum', kwargs={"club_url_name": self.club.club_url_name})
        post_count_before = ForumPost.objects.count()
        self.post['forum'] = self.club_forum
        response = self.client.post(self.club_url, self.post, follow=True)
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200, fetch_redirect_response=True
                             )
        post_count_after = ForumPost.objects.count()
        self.assertEqual(post_count_after, post_count_before+1)

    def test_create_invalid_post(self):
        self.client.login(username=self.user.username, password="Password123")
        redirect_url = reverse('global_forum')
        post_count_before = ForumPost.objects.count()
        self.post['content'] = "x" * 1025
        self.post['forum'] = self.global_forum
        response = self.client.post(self.url, self.post, follow=True)
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200, fetch_redirect_response=True
                             )
        messages_list = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        self.assertEqual(str(messages_list[0]), "There was an error making that post, try again!")
        post_count_after = ForumPost.objects.count()
        self.assertEqual(post_count_after, post_count_before)
