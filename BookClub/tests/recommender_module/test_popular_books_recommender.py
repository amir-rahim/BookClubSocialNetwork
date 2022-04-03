"""Unit testing of the Popular Books Recommender"""
from django.test import TestCase, tag
from RecommenderModule.recommenders.popular_books_recommender import PopularBooksRecommender
from RecommenderModule.recommenders.resources.data_provider import DataProvider
from RecommenderModule.recommenders.resources.popular_books_recommender_methods import PopularBooksMethods
from RecommenderModule.recommenders.resources.library import Library
from BookClub.models import Club


@tag('recommenders')
class PopularBooksRecommenderTestCase(TestCase):
    """Popular Books Recommender Tests"""
    fixtures = [
        'BookClub/tests/fixtures/default_users.json',
        'BookClub/tests/fixtures/default_books.json',
        'BookClub/tests/fixtures/default_book_reviews.json',
        'BookClub/tests/fixtures/default_clubs.json',
        'BookClub/tests/fixtures/default_club_members.json'
    ]

    def set_up_django_based_recommender(self):
        self.club_url_name = Club.objects.get(pk=1).club_url_name
        self.popular_books_recommender = PopularBooksRecommender()
        self.popular_books_methods = PopularBooksMethods(print_status=False,
                                                         parameters={'ranking_method': 'combination'})
        self.popular_books_recommender.popular_books_methods = self.popular_books_methods

    def set_up_trainset_based_recommender(self):
        data_provider = DataProvider(get_data_from_csv=True)
        self.trainset = data_provider.get_filtered_ratings_trainset()
        self.popular_books_methods = PopularBooksMethods(trainset=self.trainset, print_status=False,
                                                         parameters={'ranking_method': 'combination'})
        self.popular_books_recommender = PopularBooksRecommender()
        self.popular_books_recommender.popular_books_methods = self.popular_books_methods
        self.user_id = self.trainset.to_raw_uid(4)

    def test_get_user_recommendations(self):
        self.set_up_trainset_based_recommender()
        recommendations1 = self.popular_books_recommender.get_user_recommendations(self.user_id)
        self.assertEqual(len(recommendations1), 10)
        library = Library(trainset=self.trainset)
        user_read_books = library.get_list_of_books_rated_by_user(self.user_id)
        recommendations2 = self.popular_books_methods.get_recommendations_from_average_and_median(
            read_books=user_read_books)
        self.assertEqual(recommendations1, recommendations2)

    def test_get_user_recommendations_wrong_user_id(self):
        self.set_up_trainset_based_recommender()
        recommendations = self.popular_books_recommender.get_user_recommendations("X")
        self.assertEqual(len(recommendations), 10)

    def test_get_club_recommendations(self):
        self.set_up_django_based_recommender()
        recommendations1 = self.popular_books_recommender.get_club_recommendations(self.club_url_name)
        self.assertEqual(len(recommendations1), 10)
        library = Library()
        club_read_books = library.get_list_of_books_rated_by_club(self.club_url_name)
        recommendations2 = self.popular_books_methods.get_recommendations_from_average_and_median(
            read_books=club_read_books)
        self.assertEqual(recommendations1, recommendations2)

    def test_get_club_recommendations_wrong_club_url_name(self):
        self.set_up_django_based_recommender()
        recommendations = self.popular_books_recommender.get_club_recommendations("-")
        self.assertEqual(len(recommendations), 10)

    def test_get_number_of_recommendable_books(self):
        self.set_up_trainset_based_recommender()
        number_of_recommendable_books_1 = self.popular_books_recommender.get_number_of_recommendable_books()
        number_of_recommendable_books_2 = self.popular_books_methods.get_number_of_recommendable_books()
        self.assertEqual(number_of_recommendable_books_1, number_of_recommendable_books_2)
