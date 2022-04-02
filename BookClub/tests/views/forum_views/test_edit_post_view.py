from django.test import TestCase, tag
from django.urls import reverse

from BookClub.models import User, ForumPost, Club
from BookClub.tests.helpers import reverse_with_next


@tag('forum', 'edit_post')
class EditPostViewTestCase(TestCase):
    """Tests of the Edit Posts view."""

    fixtures = [
        'BookClub/tests/fixtures/default_users.json',
        'BookClub/tests/fixtures/default_clubs.json',
        'BookClub/tests/fixtures/default_memberships.json',
        'BookClub/tests/fixtures/default_forum.json',
        'BookClub/tests/fixtures/default_posts.json',
    ]

    def setUp(self):
        self.user = User.objects.get(username="johndoe")
        self.non_user = User.objects.get(pk=7)
        self.club = Club.objects.get(pk=1)
        self.my_post = ForumPost.objects.get(pk=1)
        self.other_post = ForumPost.objects.get(pk=2)
        self.club_post = ForumPost.objects.get(pk=4)
        self.my_url = reverse('edit_forum_post', kwargs={'post_id': self.my_post.id})
        self.other_url = reverse('edit_forum_post', kwargs={'post_id': self.other_post.id})
        self.club_url = reverse('edit_forum_post', kwargs={'club_url_name': self.club.club_url_name, 'post_id': self.club_post.id})
        self.edit = {
            "content": "HELLO, HOW DO YOU DO!",
        }

    def test_edit_post_url(self):
        self.assertEqual(self.my_url, '/forum/'+str(self.my_post.pk)+'/edit/')

    def test_edit_other_post_url(self):
        self.assertEqual(self.other_url, '/forum/'+str(self.other_post.pk)+'/edit/')

    def test_edit_club_post_url(self):
        self.assertEqual(self.club_url, '/club/'+str(self.club.club_url_name)+'/forum/'+str(self.club_post.id)+'/edit/')

    def test_redirect_when_not_logged_in(self):
        redirect_url = reverse_with_next('login', self.my_url)
        response = self.client.post(self.my_url, self.edit, follow=True)
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200, fetch_redirect_response=True
                             )
        self.assertTemplateUsed(response, 'authentication/login.html')

    def test_redirect_club_when_not_logged_in(self):
        redirect_url = reverse_with_next('login', self.club_url)
        response = self.client.post(self.club_url, self.edit, follow=True)
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200, fetch_redirect_response=True
                             )
        self.assertTemplateUsed(response, 'authentication/login.html')

    def test_redirect_when_not_creator(self):
        self.client.login(username=self.user.username, password="Password123")
        redirect_url = reverse('global_forum')
        response = self.client.post(self.other_url, self.edit, follow=True)
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200, fetch_redirect_response=True
                             )

    def test_redirect_non_existing_id(self):
        self.client.login(username=self.user.username, password="Password123")
        url = reverse('edit_forum_post', kwargs={'post_id': 555})
        redirect_url = reverse('global_forum')
        response = self.client.post(url, self.edit, follow=True)
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200, fetch_redirect_response=True
                             )

    def test_redirect_club_non_existing_id(self):
        self.client.login(username=self.user.username, password="Password123")
        url = reverse('edit_forum_post', kwargs={'club_url_name': self.club.club_url_name, 'post_id': 555})
        redirect_url = reverse('club_forum', kwargs={'club_url_name': self.club.club_url_name})
        response = self.client.post(url, self.edit, follow=True)
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200, fetch_redirect_response=True
                             )

    def test_edit_post_when_not_logged_in(self):
        redirect_url = reverse_with_next('login', self.my_url)
        response = self.client.post(self.my_url, self.edit, follow=True)
        post = ForumPost.objects.get(pk=1)
        self.assertEqual(post.content, "Lorem Ipsum is simply dummy text of the printing and typesetting industry. "
                                       "Lorem Ipsum has been the industrial standard dummy text ever since the 1500s, "
                                       "when an unknown printer took a galley of type and scrambled it to make a type "
                                       "specimen book.")

    def test_edit_post_when_not_creator(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.post(self.other_url, self.edit, follow=True)
        post = ForumPost.objects.get(pk=2)
        self.assertEqual(post.content, "Contrary to popular belief, Lorem Ipsum is not simply random text. It has "
                                       "roots in a piece of classical Latin literature from 45 BC, making it over "
                                       "2000 years old.")

    def test_edit_club_post_when_non_member(self):
        self.client.login(username=self.non_user.username, password="Password123")
        response = self.client.post(self.club_url, self.edit, follow=True)
        post = ForumPost.objects.get(pk=4)
        self.assertEqual(post.content, "... qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit...")

    def test_edit_post_when_creator(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.post(self.my_url, self.edit, follow=True)
        post = ForumPost.objects.get(pk=1)
        self.assertEqual(post.content, "HELLO, HOW DO YOU DO!")

    def test_post_details_show(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.my_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'forum/edit_forum_post.html')
        self.assertContains(response, "Lorem Ipsum")
        self.assertContains(response, "Lorem Ipsum is simply dummy text of the printing and typesetting industry. "
                                      "Lorem Ipsum has been the industrial standard dummy text ever since the "
                                      "1500s, when an unknown printer took a galley of type and scrambled it to make "
                                      "a type specimen book.")
        self.assertContains(response, "Posted by: johndoe")

    def test_club_post_details_show(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.club_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'forum/edit_forum_post.html')
        self.assertContains(response, "Latin Quota")
        self.assertContains(response, "... qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit...")
        self.assertContains(response, "Posted by: johndoe")
