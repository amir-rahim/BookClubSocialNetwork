"""Unit testing of Recommendation Models"""
from django.forms import ValidationError
from django.test import TestCase, tag

from BookClub.models import UserRecommendations, ClubRecommendations, BookReview, Club, User


@tag('models', 'recommendations')
class AbstractRecommendationTestCase(TestCase):
    """Abstract Recommendations Model, Fields, Validation and Methods Testing"""
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


@tag('models', 'recommendations')
class UserRecommendationTestCase(TestCase):
    """User Recommendations Model, Fields, Validation and Methods Testing"""
    fixtures = [
        'BookClub/tests/fixtures/default_users.json',
        'BookClub/tests/fixtures/default_books.json',
        'BookClub/tests/fixtures/default_book_reviews.json',
    ]

    def setUp(self):
        self.user1 = User.objects.get(pk=1)
        self.recommendation = UserRecommendations.objects.create(
            user=self.user1)

    def test_user_cannot_be_none(self):
        self.recommendation.user = None
        with self.assertRaises(ValidationError):
            self.recommendation.full_clean()

    def test_recommendation_set_as_modified_on_review_update(self):
        self.recommendation.modified = False
        self.recommendation.save()
        review = BookReview.objects.get(pk=1)
        review.book_rating = 5
        review.save()
        self.recommendation.refresh_from_db()
        self.assertTrue(self.recommendation.modified)


@tag('models', 'recommendations')
class ClubRecommendationsTestCase(TestCase):
    """Club Recommendations Model, Fields, Validation and Methods Testing"""
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
