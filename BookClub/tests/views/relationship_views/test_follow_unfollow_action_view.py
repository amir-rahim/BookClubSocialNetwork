"""Tests of the FollowUser view."""
from django.test import TestCase, tag
from django.urls import reverse

from BookClub.models import User, UserToUserRelationship
from BookClub.tests.helpers import LogInTester, reverse_with_next


@tag("views", "relationship_views", "un_follow")
class FollowUserViewTestCase(TestCase, LogInTester):
    """Tests of the FollowUser view."""

    fixtures = [
        'BookClub/tests/fixtures/default_users.json',
        'BookClub/tests/fixtures/default_relationships.json',
    ]

    def setUp(self):
        self.users = []
        self.users.append(User.objects.get(pk=1))
        self.users.append(User.objects.get(pk=2))
        self.users.append(User.objects.get(pk=3))

        self.urls = []
        self.urls.append(reverse('follow_user', kwargs={'username': self.users[0].username}))
        self.urls.append(reverse('follow_user', kwargs={'username': self.users[1].username}))
        self.urls.append(reverse('follow_user', kwargs={'username': self.users[2].username}))

        self.data = {}

    def user_follows(self, source, target):
        source_user = self.users[source]
        target_user = self.users[target]
        return UserToUserRelationship.objects.filter(source_user=source_user, target_user=target_user).exists()

    def ajax_get(self, url, **kwargs):
        kwargs['HTTP_X_REQUESTED_WITH'] = 'XMLHttpRequest'
        return self.client.get(url, **kwargs)

    def ajax_post(self, url, payload, **kwargs):
        kwargs['HTTP_X_REQUESTED_WITH'] = 'XMLHttpRequest'
        return self.client.post(url, payload, **kwargs)

    def test_url(self):
        self.assertEqual(self.urls[0], f'/profile/{self.users[0].username}/follow/')

    def test_get_redirects_when_not_logged_in(self):
        self.assertFalse(self._is_logged_in())
        user0_followers_count_before = UserToUserRelationship.objects.filter(target_user=self.users[0]).count()
        redirect_url = reverse_with_next('login', self.urls[0])
        response = self.client.get(self.urls[0], follow=True)
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200, fetch_redirect_response=True
                             )
        self.assertTemplateUsed(response, 'login.html')
        user0_followers_count_after = UserToUserRelationship.objects.filter(target_user=self.users[0]).count()
        self.assertEqual(user0_followers_count_after, user0_followers_count_before)

    def test_post_redirects_when_not_logged_in(self):
        self.assertFalse(self._is_logged_in())
        user0_followers_count_before = UserToUserRelationship.objects.filter(target_user=self.users[0]).count()
        redirect_url = reverse_with_next('login', self.urls[0])
        response = self.client.post(self.urls[0], self.data, follow=True)
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200, fetch_redirect_response=True
                             )
        self.assertTemplateUsed(response, 'login.html')
        user0_followers_count_after = UserToUserRelationship.objects.filter(target_user=self.users[0]).count()
        self.assertEqual(user0_followers_count_after, user0_followers_count_before)

    def test_get_redirects_when_request_is_not_ajax(self):
        self.client.login(username=self.users[0].username, password='Password123')
        user2_followers_count_before = UserToUserRelationship.objects.filter(target_user=self.users[2]).count()
        redirect_url = reverse('user_profile', kwargs={'username': self.users[2].username})
        response = self.client.get(self.urls[2], follow=True)
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200, fetch_redirect_response=True
                             )
        self.assertTemplateUsed(response, 'user_dashboard.html')
        user2_followers_count_after = UserToUserRelationship.objects.filter(target_user=self.users[2]).count()
        self.assertEqual(user2_followers_count_after, user2_followers_count_before)

    def test_post_redirects_when_request_is_not_ajax(self):
        self.client.login(username=self.users[0].username, password='Password123')
        user2_followers_count_before = UserToUserRelationship.objects.filter(target_user=self.users[2]).count()
        redirect_url = reverse('user_profile', kwargs={'username': self.users[2].username})
        response = self.client.post(self.urls[2], self.data, follow=True)
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200, fetch_redirect_response=True
                             )
        self.assertTemplateUsed(response, 'user_dashboard.html')
        user2_followers_count_after = UserToUserRelationship.objects.filter(target_user=self.users[2]).count()
        self.assertEqual(user2_followers_count_after, user2_followers_count_before)


    def test_ajax_get_returns_404_for_non_existing_username(self):
        self.client.login(username=self.users[0].username, password='Password123')
        user2_followers_count_before = UserToUserRelationship.objects.filter(target_user=self.users[2]).count()
        response = self.ajax_get(reverse('follow_user', kwargs={'username': self.users[2].username + 'x'}))
        self.assertEqual(response.status_code, 404)
        user2_followers_count_after = UserToUserRelationship.objects.filter(target_user=self.users[2]).count()
        self.assertEqual(user2_followers_count_after, user2_followers_count_before)

    def test_ajax_post_returns_404_for_non_existing_username(self):
        self.client.login(username=self.users[0].username, password='Password123')
        user2_followers_count_before = UserToUserRelationship.objects.filter(target_user=self.users[2]).count()
        response = self.ajax_post(reverse('follow_user', kwargs={'username': self.users[2].username + 'x'}), self.data)
        self.assertEqual(response.status_code, 404)
        user2_followers_count_after = UserToUserRelationship.objects.filter(target_user=self.users[2]).count()
        self.assertEqual(user2_followers_count_after, user2_followers_count_before)

    def test_ajax_get_returns_correctly(self):
        self.client.login(username=self.users[0].username, password='Password123')
        user2_followers_count_before = UserToUserRelationship.objects.filter(target_user=self.users[2]).count()
        response = self.ajax_get(self.urls[2])
        self.assertEqual(response.status_code, 200)
        response_dict = response.json()
        self.assertIn('target_user_username', response_dict)
        self.assertIn('is_followed', response_dict)
        self.assertEqual(response_dict['is_followed'], self.user_follows(0, 2))
        user2_followers_count_after = UserToUserRelationship.objects.filter(target_user=self.users[2]).count()
        self.assertEqual(user2_followers_count_after, user2_followers_count_before)

    def test_ajax_post_creates_relationship_if_did_not_exist_and_returns_correctly(self):
        self.client.login(username=self.users[0].username, password='Password123')
        user2_followers_count_before = UserToUserRelationship.objects.filter(target_user=self.users[2]).count()
        response = self.ajax_post(self.urls[2], self.data)
        self.assertEqual(response.status_code, 200)
        response_dict = response.json()
        self.assertIn('target_user_username', response_dict)
        self.assertIn('is_followed', response_dict)
        self.assertEqual(response_dict['is_followed'], self.user_follows(0, 2))
        user2_followers_count_after = UserToUserRelationship.objects.filter(target_user=self.users[2]).count()
        self.assertEqual(user2_followers_count_after, user2_followers_count_before + 1)

    def test_ajax_post_deletes_relationship_if_already_existed_and_returns_correctly(self):
        self.client.login(username=self.users[0].username, password='Password123')
        user1_followers_count_before = UserToUserRelationship.objects.filter(target_user=self.users[1]).count()
        response = self.ajax_post(self.urls[1], self.data)
        self.assertEqual(response.status_code, 200)
        response_dict = response.json()
        self.assertIn('target_user_username', response_dict)
        self.assertIn('is_followed', response_dict)
        self.assertEqual(response_dict['is_followed'], self.user_follows(0, 1))
        user1_followers_count_after = UserToUserRelationship.objects.filter(target_user=self.users[1]).count()
        self.assertEqual(user1_followers_count_after, user1_followers_count_before - 1)
