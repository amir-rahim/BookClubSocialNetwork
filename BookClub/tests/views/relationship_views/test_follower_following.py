from django.test import TestCase, tag
from django.urls import reverse
from BookClub.models import User, UserToUserRelationship

@tag('view','list','following','followee')
class FollowingFolloweeTestCase(TestCase):

    fixtures = [
        'BookClub/tests/fixtures/default_users.json',
        'BookClub/tests/fixtures/default_relationships.json',
    ]

    # test no followers
    # test one follower
    # test no followees
    # test no followees

    def setUp(self):
        self.user1 = User.objects.get(pk=1)
        self.user2 = User.objects.get(pk=2)
        self.following_relation = UserToUserRelationship.objects.get(pk=1)
        self.follower_relation = UserToUserRelationship.objects.get(pk=2)
        self.url = reverse('user_following', kwargs={'username':self.user1.username})

    def test_url(self):
        self.assertEqual(self.url, '/profile/johndoe/following/')

    def test_no_followers(self):
        self.following_relation.delete()
        self.follower_relation.delete()
        self.client.login(username=self.user1.username, password="Password123")
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'following_followers.html')
        self.assertContains(response,"There are no followers for this user.")

    def test_1_follower(self):
        self.following_relation.delete()
        self.client.login(username=self.user1.username, password="Password123")
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'following_followers.html')
        self.assertContains(response,"1 follower")
        self.assertContains(response, self.user2.username)

    def test_no_followee(self):
        self.following_relation.delete()
        self.follower_relation.delete()
        self.client.login(username=self.user1.username, password="Password123")
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'following_followers.html')
        self.assertContains(response, "This user isn't following anyone")


    def test_1_followee(self):
        self.follower_relation.delete()
        self.client.login(username=self.user1.username, password="Password123")
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'following_followers.html')
        self.assertContains(response, "1 following")
        self.assertContains(response, self.user2.username)
