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
        self.rel1 = UserToUserRelationship.objects.get(pk=1)
        self.url = reverse('user_following', kwargs={'username':self.user1.username})
        
    def test_url(self):
        self.assertEqual(self.url, '/profile/johndoe/following/')