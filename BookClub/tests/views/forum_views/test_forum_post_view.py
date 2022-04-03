"""Unit testing of the Forum Post view"""
from django.test import TestCase, tag
from django.urls import reverse

from BookClub.models import User, ForumPost, Club, Forum


@tag('views', 'forum', 'forum_post')
class ForumPostViewTestCase(TestCase):
    """Tests of the Forum Post view."""

    fixtures = [
        'BookClub/tests/fixtures/default_users.json',
        'BookClub/tests/fixtures/default_clubs.json',
        'BookClub/tests/fixtures/default_memberships.json',
        'BookClub/tests/fixtures/default_forum.json',
        'BookClub/tests/fixtures/default_posts.json',
        'BookClub/tests/fixtures/default_comments.json',
    ]

    def setUp(self):
        self.my_post = ForumPost.objects.get(pk=1)
        self.my_url = reverse('forum_post', kwargs={'post_id': self.my_post.pk})
        self.other_post = ForumPost.objects.get(pk=2)
        self.other_url = reverse('forum_post', kwargs={'post_id': self.other_post.pk})
        self.user = User.objects.get(username="johndoe")
        self.other_user = User.objects.get(pk=2)
        self.club = Club.objects.get(pk=1)
        self.other_club = Club.objects.get(pk=3)
        
        self.club_post = ForumPost.objects.get(pk=4)

        Forum.objects.create(
                title='forum for other club',
                associated_with=self.other_club
        )

    def test_my_forum_post_url(self):
        self.assertEqual(self.my_url, '/forum/' + str(self.my_post.id) + '/')

    def test_other_forum_post_url(self):
        self.assertEqual(self.other_url, '/forum/' + str(self.other_post.id) + '/')

    def test_get_forum_post_not_logged_in(self):
        response = self.client.get(self.my_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'forum/forum_post.html')

    def test_get_forum_post_logged_in(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.my_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'forum/forum_post.html')

    def test_get_other_forum_post_logged_in(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.other_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'forum/forum_post.html')

    def test_get_post_does_not_exist(self):
        ForumPost.objects.all().delete()
        response = self.client.get(self.my_url)
        self.assertEqual(response.status_code, 404)

    def test_post_details_show(self):
        response = self.client.get(self.my_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'forum/forum_post.html')
        self.assertContains(response, "Lorem Ipsum")
        self.assertContains(response, "Lorem Ipsum is simply dummy text of the printing and typesetting industry. "
                                      "Lorem Ipsum has been the industrial standard dummy text ever since the "
                                      "1500s, when an unknown printer took a galley of type and scrambled it to make "
                                      "a type specimen book.")
        self.assertContains(response, "johndoe")

    def test_invalid_post_for_club_post(self):
        self.client.login(username=self.other_user.username, password="Password123")
        url = reverse('forum_post', kwargs={'club_url_name': self.other_club.club_url_name, 'post_id': self.club_post.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_has_no_buttons_not_own_post(self):
        response = self.client.get(self.my_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'forum/forum_post.html')
        self.assertNotContains(response, "<a href=\"" + self.my_url + "edit/\">")
        self.assertNotContains(response,
                               "<button class=\"button is-danger is-rounded\" aria-label=\"Delete Post\" type=\"submit\">")

    def test_has_buttons_own_post(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.my_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'forum/forum_post.html')
        self.assertContains(response, "<a href=\"" + self.my_url + "edit/\">")

    def test_comments_shown(self):
        response = self.client.get(self.my_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'forum/forum_post.html')
        comments = list(response.context['post'].get_comments())
        self.assertEqual(len(comments), 2)
        self.assertContains(response, "Wow this topic is so interesting, damn.")

    def test_no_comments_shown(self):
        response = self.client.get(self.other_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'forum/forum_post.html')
        comments = list(response.context['post'].get_comments())
        self.assertEqual(len(comments), 0)
        self.assertContains(response, "<i>There are no comments for this post. Comment using the reply button on the post.</i>")

    def test_view_returns_404_when_non_existing_post_of_global_forum_is_requested(self):
        wrong_post_id = 100
        self.assertFalse(ForumPost.objects.filter(pk=wrong_post_id).exists())
        wrong_post_id_url = reverse('forum_post', kwargs={'post_id': 100})
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(wrong_post_id_url)
        self.assertEqual(response.status_code, 404)

    def test_view_returns_404_when_non_existing_post_of_club_forum_is_requested(self):
        wrong_post_id = 100
        self.assertFalse(ForumPost.objects.filter(pk=wrong_post_id).exists())
        wrong_post_id_url = reverse('forum_post', kwargs={'post_id': 100, 'club_url_name': 'Johnathan_Club'})
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(wrong_post_id_url)
        self.assertEqual(response.status_code, 404)
