"""Unit Testing of the Follower/Following User view."""
from django.test import TestCase, tag
from django.urls import reverse
from BookClub.models import User, UserToUserRelationship


@tag('view', 'following', 'followee')
class FollowingFolloweeTestCase(TestCase):
    """Tests of the Follow User view."""
    fixtures = [
        'BookClub/tests/fixtures/default_users.json',
        'BookClub/tests/fixtures/default_relationships.json',
    ]

    def setUp(self):
        self.user1 = User.objects.get(pk=1)
        self.user2 = User.objects.get(pk=2)
        self.following_relation = UserToUserRelationship.objects.get(pk=1)
        self.follower_relation = UserToUserRelationship.objects.get(pk=2)
        self.url = reverse('user_following', kwargs={'username': self.user1.username})

    def test_url(self):
        self.assertEqual(self.url, '/profile/johndoe/following/')

    def test_no_followers(self):
        self.following_relation.delete()
        self.follower_relation.delete()
        self.client.login(username=self.user1.username, password="Password123")
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'user/following_followers.html')
        self.assertContains(response, "There are no followers for this user.")

    def test_1_follower(self):
        self.following_relation.delete()
        self.client.login(username=self.user1.username, password="Password123")
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'user/following_followers.html')
        self.assertContains(response, "1 Follower")
        self.assertContains(response, self.user2.username)

    def test_no_followee(self):
        self.following_relation.delete()
        self.follower_relation.delete()
        self.client.login(username=self.user1.username, password="Password123")
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'user/following_followers.html')
        self.assertContains(response, "This user isn't following anyone")

    def test_1_followee(self):
        self.follower_relation.delete()
        self.client.login(username=self.user1.username, password="Password123")
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'user/following_followers.html')
        self.assertContains(response, "1 Following")
        self.assertContains(response, self.user2.username)

    def test_view_returns_valid_response_when_user_is_checking_own_followers_and_followees(self):
        url = '/user/following/'
        self.client.login(username=self.user1.username, password="Password123")
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'user/following_followers.html')
        self.assertContains(response, "1 Following")
        self.assertContains(response, self.user2.username)
