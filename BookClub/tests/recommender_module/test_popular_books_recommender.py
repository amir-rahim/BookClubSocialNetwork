from django.test import TestCase, tag
from RecommenderModule.recommenders.popular_books_recommender import PopularBooksRecommender
from RecommenderModule.recommenders.resources.data_provider import DataProvider
from RecommenderModule.recommenders.resources.popular_books_recommender_methods import PopularBooksMethods
from RecommenderModule.recommenders.resources.library import Library

@tag('recommenders')
class PopularBooksRecommenderTestCase(TestCase):

    def setUp(self):
        data_provider = DataProvider(get_data_from_csv=True)
        self.trainset = data_provider.get_filtered_ratings_trainset()
        self.popular_books_methods = PopularBooksMethods(trainset=self.trainset, print_status=False)
        self.popular_books_recommender = PopularBooksRecommender()
        self.popular_books_recommender.popular_books_methods = self.popular_books_methods
        self.user_id = self.trainset.to_raw_uid(4)

    def test_get_recommendations(self):
        recommendations1 = self.popular_books_recommender.get_recommendations(self.user_id)
        self.assertEqual(len(recommendations1), 10)
        library = Library(trainset=self.trainset)
        user_read_books = library.get_all_books_rated_by_user(self.user_id)
        recommendations2 = self.popular_books_methods.get_recommendations_from_median(user_read_books=user_read_books)
        self.assertEqual(recommendations1, recommendations2)

    def test_get_recommendations_wrong_user_id(self):
        recommendations = self.popular_books_recommender.get_recommendations("X")
        self.assertEqual(len(recommendations), 10)