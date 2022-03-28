from django.test import TestCase, tag
from django.urls import reverse

from BookClub.models import User, ForumPost, Club
from BookClub.tests.helpers import reverse_with_next


@tag('forum', 'forum_view')
class ForumViewTestCase(TestCase):
    """Tests of the Forum view."""

    fixtures = [
        'BookClub/tests/fixtures/default_users.json',
        'BookClub/tests/fixtures/default_forum.json',
        'BookClub/tests/fixtures/default_posts.json',
        'BookClub/tests/fixtures/default_clubs.json',
        'BookClub/tests/fixtures/default_memberships.json',
    ]

    def setUp(self):
        self.url = reverse('global_forum')
        self.user = User.objects.get(username="johndoe")
        self.club = Club.objects.get(pk=1)
        self.club_url = reverse('club_forum', kwargs={"club_url_name": self.club.club_url_name})

    def test_club_forum_url(self):
        self.assertEqual(self.club_url, '/club/'+self.club.club_url_name+'/forum/')

    def test_global_forum_url(self):
        self.assertEqual(self.url, '/forum/')

    def test_get_forum_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'forum/forums.html')

    def test_get_club_forum_not_logged_in(self):
        redirect_url = reverse_with_next('login', self.club_url)
        response = self.client.get(self.club_url)
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200, fetch_redirect_response=True
                             )

    def test_get_forum_logged_in(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'forum/forums.html')

    def test_get_club_forum_logged_in(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.club_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'forum/forums.html')

    def test_posts_show(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'forum/forums.html')
        posts = list(response.context['posts'])
        self.assertEqual(len(posts), 3)

    def test_club_posts_show(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.club_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'forum/forums.html')
        posts = list(response.context['posts'])
        self.assertEqual(len(posts), 1)

    def test_no_posts(self):
        ForumPost.objects.all().delete()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'forum/forums.html')
        posts = list(response.context['posts'])
        self.assertEqual(len(posts), 0)
        self.assertContains(response, "There are no posts at the moment. Be first to post!")

    def test_no_club_posts(self):
        self.client.login(username=self.user.username, password="Password123")
        ForumPost.objects.all().delete()
        response = self.client.get(self.club_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'forum/forums.html')
        posts = list(response.context['posts'])
        self.assertEqual(len(posts), 0)
        self.assertContains(response, "There are no posts at the moment. Be first to post!")

    def test_post_details_show(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'forum/forums.html')
        self.assertContains(response, "Lorem Ipsum")
        self.assertContains(response, "Lorem Ipsum is simply dummy text of the printing and typesetting industry. ")
        self.assertContains(response, "Posted by: johndoe")
