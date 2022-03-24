from django.forms import ValidationError
from BookClub.models import UserRecommendations, ClubRecommendations
from django.test import TestCase, tag
from BookClub.models.club import Club


from BookClub.models.user import User

@tag('recommendations','user')
class AbstractRecommendationTestCase(TestCase):
    
    fixtures = ['BookClub/tests/fixtures/default_users.json']
    
    def setUp(self):
        self.user1 = User.objects.get(pk=1)
        self.recommendation = UserRecommendations.objects.create(user=self.user1)
        
    def test_defaults(self):
        self.assertEqual(self.recommendation.modified, True)
        self.assertEqual(self.recommendation.recommendations, [])
        
    def test_modified_not_null(self):
        self.recommendation.modified = None
        with self.assertRaises(ValidationError):
            self.recommendation.full_clean()
    
    def test_recommendation_not_null(self):
        self.recommendation.recommendations = None
        with self.assertRaises(ValidationError):
            self.recommendation.full_clean()
            
    def test_recommendation_serialises_and_returns_correctly(self):
        testlist = ["Test!"]
        self.recommendation.recommendations = testlist
        self.recommendation.save()
        self.recommendation.refresh_from_db()
        self.assertEqual(self.recommendation.recommendations, testlist)
        

@tag('recommendations', 'user')
class UserRecommendationTestCase(TestCase):

    fixtures = ['BookClub/tests/fixtures/default_users.json']

    def setUp(self):
        self.user1 = User.objects.get(pk=1)
        self.recommendation = UserRecommendations.objects.create(
            user=self.user1)
        
    def test_user_cannot_be_none(self):
        self.recommendation.user = None
        with self.assertRaises(ValidationError):
            self.recommendation.full_clean()


@tag('recommendations', 'club')
class ClubRecommendationsTestCase(TestCase):

    fixtures = ['BookClub/tests/fixtures/default_users.json',
                'BookClub/tests/fixtures/default_clubs.json']

    def setUp(self):
        self.club = Club.objects.get(pk=1)
        self.recommendation = ClubRecommendations.objects.create(
            club=self.club)

    def test_user_cannot_be_none(self):
        self.recommendation.club = None
        with self.assertRaises(ValidationError):
            self.recommendation.full_clean()
