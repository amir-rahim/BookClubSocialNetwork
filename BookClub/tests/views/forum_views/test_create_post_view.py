from django.test import TestCase, tag
from django.urls import reverse
from BookClub.models import User, Forum, ForumPost
from BookClub.tests.helpers import reverse_with_next


@tag('forum', 'create')
class CreatePostViewTestCase(TestCase):
    """Tests of the Create Posts view."""

    fixtures = [
        'BookClub/tests/fixtures/default_users.json',
        'BookClub/tests/fixtures/default_empty_forum.json',
    ]

    def setUp(self):
        self.url = reverse('create_forum_post')
        self.user = User.objects.get(username="johndoe")
        self.post = {
            "title": "Lorem Ipsum",
            "content": "HELLO, HOW DO YOU DO!",
        }

    def test_create_post_url(self):
        self.client.login(username=self.user.username, password="Password123")
        self.assertEqual(self.url, '/forum/post/')

    def test_redirect_when_not_logged_in(self):
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.post(self.url, self.post, follow=True)
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
        self.assertTemplateUsed(response, 'login.html')
        post_count_after = ForumPost.objects.count()
        self.assertEqual(post_count_after, post_count_before)

    def test_create_post_when_logged_in(self):
        self.client.login(username=self.user.username, password="Password123")
        redirect_url = reverse('global_forum')
        post_count_before = ForumPost.objects.count()
        response = self.client.post(self.url, self.post, follow=True)
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200, fetch_redirect_response=True
                             )
        post_count_after = ForumPost.objects.count()
        self.assertEqual(post_count_after, post_count_before+1)
