"""Unit testing of Content Based Recommender"""
from django.test import TestCase, tag
from RecommenderModule.recommenders.resources.content_based_recommender_methods import ContentBasedRecommenderMethods
from RecommenderModule.recommenders.content_based_recommender import ContentBasedRecommender
from BookClub.models import User, Club


@tag('recommenders')
class ContentBasedRecommenderTestCase(TestCase):
    """Content Based Recommender Testing"""
    fixtures = [
        'BookClub/tests/fixtures/default_content_based_books.json',
        'BookClub/tests/fixtures/default_users.json',
        'BookClub/tests/fixtures/default_content_based_book_reviews.json',
        'BookClub/tests/fixtures/default_clubs.json',
        'BookClub/tests/fixtures/default_content_based_club_members.json'
    ]

    def setUp(self):
        self.content_based_methods = ContentBasedRecommenderMethods(retraining=True, get_data_from_csv=True)
        self.content_based_recommender = ContentBasedRecommender()
        self.content_based_recommender.content_based_methods = self.content_based_methods
        self.user_id = User.objects.get(pk=1).username
        self.club_url_name = Club.objects.get(pk=1).club_url_name

    def test_get_user_recommendations(self):
        recommendations1 = self.content_based_recommender.get_user_recommendations(self.user_id)
        self.assertEqual(len(recommendations1), 10)
        recommendations2 = self.content_based_methods.get_recommendations_positive_ratings_only_from_user_id(
            self.user_id)
        self.assertEqual(recommendations1, recommendations2)

    def test_get_user_recommendations_wrong_user_id(self):
        recommendations = self.content_based_recommender.get_user_recommendations("X")
        self.assertEqual(recommendations, [])

    def test_get_club_recommendations(self):
        recommendations1 = self.content_based_recommender.get_club_recommendations(self.club_url_name)
        self.assertEqual(len(recommendations1), 10)
        recommendations2 = self.content_based_methods.get_recommendations_positive_ratings_only_from_club_url_name(
            self.club_url_name)
        self.assertEqual(recommendations1, recommendations2)

    def test_get_club_recommendations_wrong_club_url_name(self):
        recommendations = self.content_based_recommender.get_club_recommendations("-")
        self.assertEqual(recommendations, [])

    def test_get_number_of_recommendable_books(self):
        number_of_recommendable_books = self.content_based_recommender.get_number_of_recommendable_books()
        self.assertEqual(number_of_recommendable_books, len(self.content_based_methods.book_content_list))
