from django.test import TestCase, tag
from BookClub.models import User, BookReview
from BookClub.recommender_module import recommendations_provider

@tag('recommenders')
class RecommendersTestCase(TestCase):

    fixtures = ['BookClub/tests/fixtures/default_users.json']

    def setUp(self):
        self.user = User.objects.get(username='johndoe')


    def test_get_popularity_recommendations(self):
        recommendations = recommendations_provider.get_popularity_recommendations(self.user)
        self.assertEqual(len(recommendations), 10)
        self.assertTrue(all(isinstance(isbn, str) for isbn in recommendations))

    def test_get_popularity_recommendations_exclude_books_read(self):
        pass

    def test_get_books_read_by_user(self):
        pass

    def test_get_books_read_by_user_no_book(self):
        user_read_books = recommendations_provider.get_user_read_books(self.user)
        self.assertEqual(user_read_books, [])
