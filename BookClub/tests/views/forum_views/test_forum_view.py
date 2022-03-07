from django.test import TestCase, tag
from django.urls import reverse
from BookClub.models import User, Forum, ForumPost


@tag('forum')
class ForumViewTestCase(TestCase):
    """Tests of the Forum view."""

    fixtures = [
        'BookClub/tests/fixtures/default_users.json',
        'BookClub/tests/fixtures/default_forum.json',
        'BookClub/tests/fixtures/default_posts.json',
    ]

    def setUp(self):
        self.url = reverse('global_forum')
        self.user = User.objects.get(username="johndoe")

    def test_forum_url(self):
        self.assertEqual(self.url, '/forum/')

    def test_get_forum_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'global_forum.html')

    def test_get_forum_logged_in(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'global_forum.html')

    def test_posts_show(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'global_forum.html')
        posts = list(response.context['posts'])
        self.assertEqual(len(posts), 3)

    def test_no_posts(self):
        ForumPost.objects.all().delete()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'global_forum.html')
        posts = list(response.context['posts'])
        self.assertEqual(len(posts), 0)
        self.assertContains(response, "<p style=\"text-align: center\">There are no posts at the moment. Be first to "
                                      "post!</p>")

    def test_post_details_show(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'global_forum.html')
        self.assertContains(response, "Lorem Ipsum")
        self.assertContains(response, "Lorem Ipsum is simply dummy text of the printing and typesetting industry. ")
        self.assertContains(response, "Posted by: johndoe")
