"""Unit testing of the Delete Post view"""
from django.test import TestCase, tag
from django.urls import reverse

from BookClub.models import User, ForumPost, Club
from BookClub.tests.helpers import reverse_with_next


@tag('views', 'forum', 'delete_post')
class DeletePostViewTestCase(TestCase):
    """Tests of the Delete Posts view."""

    fixtures = [
        'BookClub/tests/fixtures/default_users.json',
        'BookClub/tests/fixtures/default_clubs.json',
        'BookClub/tests/fixtures/default_memberships.json',
        'BookClub/tests/fixtures/default_forum.json',
        'BookClub/tests/fixtures/default_posts.json',
    ]

    def setUp(self):
        self.user = User.objects.get(username="johndoe")
        self.non_member = User.objects.get(pk=2)
        self.club = Club.objects.get(pk=1)
        self.my_post = ForumPost.objects.get(pk=1)
        self.other_post = ForumPost.objects.get(pk=2)
        self.club_post = ForumPost.objects.get(pk=4)
        self.my_url = reverse('delete_forum_post', kwargs={'post_id': self.my_post.id})
        self.other_url = reverse('delete_forum_post', kwargs={'post_id': self.other_post.id})
        self.club_url = reverse('delete_forum_post',
                                kwargs={'club_url_name': self.club.club_url_name, 'post_id': self.club_post.id})

    def test_delete_post_url(self):
        self.assertEqual(self.my_url, '/forum/'+str(self.my_post.pk)+'/delete/')

    def test_delete_post_other_url(self):
        self.assertEqual(self.other_url, '/forum/'+str(self.other_post.pk)+'/delete/')

    def test_delete_club_post_url(self):
        self.assertEqual(self.club_url, '/club/'+str(self.club.club_url_name)+'/forum/'+str(self.club_post.id)+'/delete/')

    def test_redirect_when_not_logged_in(self):
        redirect_url = reverse_with_next('login', self.my_url)
        response = self.client.post(self.my_url, follow=True)
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200, fetch_redirect_response=True
                             )
        self.assertTemplateUsed(response, 'authentication/login.html')

    def test_redirect_when_not_creator(self):
        self.client.login(username=self.user.username, password="Password123")
        redirect_url = reverse('global_forum')
        response = self.client.post(self.other_url, follow=True)
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200, fetch_redirect_response=True
                             )

    def test_redirect_when_not_member(self):
        self.client.login(username=self.non_member.username, password="Password123")
        redirect_url = reverse('club_dashboard', kwargs={'club_url_name': self.club.club_url_name})
        response = self.client.post(self.club_url, follow=True)
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200, fetch_redirect_response=True
                             )

    def test_redirect_non_existing_id(self):
        self.client.login(username=self.user.username, password="Password123")
        url = reverse('delete_forum_post', kwargs={'post_id': 555})
        redirect_url = reverse('global_forum')
        response = self.client.post(url, follow=True)
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200, fetch_redirect_response=True
                             )

    def test_delete_post_when_not_logged_in(self):
        before_count = ForumPost.objects.count()
        response = self.client.post(self.my_url, follow=True)
        after_count = ForumPost.objects.count()
        self.assertEqual(before_count, after_count)

    def test_delete_post_when_not_creator(self):
        self.client.login(username=self.user.username, password="Password123")
        before_count = ForumPost.objects.count()
        response = self.client.post(self.other_url, follow=True)
        after_count = ForumPost.objects.count()
        self.assertEqual(before_count, after_count)

    def test_delete_post_when_creator(self):
        self.client.login(username=self.user.username, password="Password123")
        before_count = ForumPost.objects.count()
        response = self.client.post(self.my_url, follow=True)
        after_count = ForumPost.objects.count()
        self.assertEqual(before_count, after_count+1)

    def test_delete_club_post_when_creator(self):
        self.client.login(username=self.user.username, password="Password123")
        before_count = ForumPost.objects.count()
        response = self.client.post(self.club_url, follow=True)
        after_count = ForumPost.objects.count()
        self.assertEqual(before_count, after_count+1)
