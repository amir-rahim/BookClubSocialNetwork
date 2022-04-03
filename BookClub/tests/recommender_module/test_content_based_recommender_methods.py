"""Unit testing of Content Based Recommender Methods"""
from django.test import TestCase, tag
from RecommenderModule.recommenders.resources.content_based_recommender_methods import ContentBasedRecommenderMethods
from BookClub.models import User, Club
import math


@tag('recommenders')
class ContentBasedRecommenderMethodsTestCase(TestCase):
    """Content Based Recommender Methods Testing"""
    fixtures = [
        'BookClub/tests/fixtures/default_content_based_books.json',
        'BookClub/tests/fixtures/default_users.json',
        'BookClub/tests/fixtures/default_content_based_book_reviews.json',
        'BookClub/tests/fixtures/default_clubs.json',
        'BookClub/tests/fixtures/default_content_based_club_members.json'
    ]

    def setUp(self):
        """data_provider = DataProvider(get_data_from_csv=True)
        self.trainset = data_provider.get_filtered_ratings_trainset()
        self.content_based_methods = ContentBasedRecommenderMethods(trainset=self.trainset, get_data_from_csv=True)
        self.user_id = self.trainset.to_raw_uid(0)
        self.library = Library(trainset=self.trainset)"""
        self.content_based_methods = ContentBasedRecommenderMethods()

    def set_up_content_based_methods_from_csv(self):
        self.content_based_methods = ContentBasedRecommenderMethods(retraining=True, get_data_from_csv=True)
        self.positive_ratings = [
            ("014029192X", 7),
            ("033030058X", 6)
        ]
        self.all_ratings = [
            ("014029192X", 7),
            ("033030058X", 6),
            ("1559585595", 3)
        ]
        self.user = User.objects.get(pk=1)
        self.club = Club.objects.get(pk=1)

    def test_compute_categories_similarity(self):
        categories1 = [1, 2, 3]
        categories2 = [2, 3, 4, 5]
        similarity = self.content_based_methods.compute_categories_similarity(categories1, categories2)
        self.assertEqual(similarity, 2 / math.sqrt(3 * 4))

    def test_compute_categories_similarity_empty_categories_list(self):
        categories1 = [1, 2, 3]
        categories2 = []
        similarity1 = self.content_based_methods.compute_categories_similarity(categories1, categories2)
        self.assertEqual(similarity1, 0)
        similarity2 = self.content_based_methods.compute_categories_similarity(categories2, categories1)
        self.assertEqual(similarity2, 0)

    def test_compute_categories_similarity_100_percent_similarity(self):
        categories1 = [1, 2, 3]
        categories2 = [2, 1, 3]
        similarity = self.content_based_methods.compute_categories_similarity(categories1, categories2)
        self.assertEqual(similarity, 1)

    def test_compute_publication_year_similarity_first_smaller(self):
        publication_year_1 = 1990
        publication_year_2 = 2010
        similarity = self.content_based_methods.compute_publication_year_similarity(publication_year_1,
                                                                                    publication_year_2)
        self.assertEqual(similarity, math.exp(-2))

    def test_compute_publication_year_similarity_second_smaller(self):
        publication_year_1 = 2010
        publication_year_2 = 1990
        similarity = self.content_based_methods.compute_publication_year_similarity(publication_year_1,
                                                                                    publication_year_2)
        self.assertEqual(similarity, math.exp(-2))

    def test_compute_publication_year_similarity_100_percent_similarity(self):
        publication_year_1 = 2010
        publication_year_2 = 2010
        similarity = self.content_based_methods.compute_publication_year_similarity(publication_year_1,
                                                                                    publication_year_2)
        self.assertEqual(similarity, 1)

    def test_get_content_similarity_between_books_using_publication_year(self):
        book_content_dict_1 = {
            "book_isbn": "014029192X",
            "categories": [1, 2, 3],
            "publication_year": 2000
        }
        book_content_dict_2 = {
            "book_isbn": "033030058X",
            "categories": [3, 2, 4, 5],
            "publication_year": 1987
        }
        similarity1 = self.content_based_methods.get_content_similarity_between_books(book_content_dict_1,
                                                                                      book_content_dict_2)
        categories_similarity = self.content_based_methods.compute_categories_similarity([1, 2, 3], [3, 2, 4, 5])
        publication_year_similarity = self.content_based_methods.compute_publication_year_similarity(2000, 1987)
        similarity2 = categories_similarity * publication_year_similarity
        self.assertEqual(similarity1, similarity2)

    def test_get_content_similarity_between_books_not_using_publication_year(self):
        book_content_dict_1 = {
            "book_isbn": "014029192X",
            "categories": [1, 2, 3],
            "publication_year": 2000
        }
        book_content_dict_2 = {
            "book_isbn": "033030058X",
            "categories": [3, 2, 4, 5],
            "publication_year": 1987
        }
        self.content_based_methods.using_publication_year = False
        similarity1 = self.content_based_methods.get_content_similarity_between_books(book_content_dict_1,
                                                                                      book_content_dict_2)
        similarity2 = self.content_based_methods.compute_categories_similarity([1, 2, 3], [3, 2, 4, 5])
        self.assertEqual(similarity1, similarity2)

    def test_get_positive_ratings_from_all_ratings(self):
        all_ratings = [
            ("014029192X", 7),
            ("033030058X", 6),
            ("1559585595", 3)
        ]
        positive_ratings_1 = self.content_based_methods.get_positive_ratings_from_all_ratings(all_ratings, min_rating=6)
        positive_ratings_2 = [
            ("014029192X", 7),
            ("033030058X", 6)
        ]
        self.assertEqual(positive_ratings_1, positive_ratings_2)

    def test_get_positive_ratings_from_all_ratings_empty_all_ratings(self):
        all_ratings = []
        positive_ratings = self.content_based_methods.get_positive_ratings_from_all_ratings(all_ratings, min_rating=6)
        self.assertEqual(positive_ratings, [])

    def test_get_recommendations_from_positive_ratings(self):
        self.set_up_content_based_methods_from_csv()
        recommendations = self.content_based_methods.get_recommendations_from_positive_ratings(self.positive_ratings,
                                                                                               self.all_ratings)
        self.assertEqual(len(recommendations), 10)
        for recommendation in recommendations:
            self.assertEqual(type(recommendation), str)
            self.assertEqual(len(recommendation), 10)

    def test_get_recommendations_from_positive_ratings_empty_positive_ratings(self):
        self.set_up_content_based_methods_from_csv()
        recommendations = self.content_based_methods.get_recommendations_from_positive_ratings([], self.all_ratings)
        self.assertEqual(recommendations, [])

    def test_get_recommendations_from_positive_ratings_does_not_contain_read_books(self):
        self.set_up_content_based_methods_from_csv()
        recommendations1 = self.content_based_methods.get_recommendations_from_positive_ratings(self.positive_ratings,
                                                                                                self.all_ratings)
        book1 = recommendations1[0]
        self.assertTrue(book1 in recommendations1)
        self.all_ratings.append((book1, 1))
        recommendations2 = self.content_based_methods.get_recommendations_from_positive_ratings(self.positive_ratings,
                                                                                                self.all_ratings)
        self.assertFalse(book1 in recommendations2)
        for i in range(9):
            self.assertEqual(recommendations1[i + 1], recommendations2[i])

    def test_get_recommendations_positive_ratings_only_from_user_id(self):
        self.set_up_content_based_methods_from_csv()
        recommendations1 = self.content_based_methods.get_recommendations_positive_ratings_only_from_user_id(
            self.user.username)
        positive_ratings = [
            ("014029192X", 7),
        ]
        all_ratings = [
            ("014029192X", 7),
            ("1559585595", 3)
        ]
        recommendations2 = self.content_based_methods.get_recommendations_from_positive_ratings(positive_ratings,
                                                                                                all_ratings)
        self.assertEqual(recommendations1, recommendations2)

    def test_get_recommendations_positive_ratings_only_from_user_id_wrong_user_id(self):
        self.set_up_content_based_methods_from_csv()
        recommendations = self.content_based_methods.get_recommendations_positive_ratings_only_from_user_id("X")
        self.assertEqual(recommendations, [])

    def test_get_recommendations_positive_ratings_only_from_club_url_name(self):
        self.set_up_content_based_methods_from_csv()
        recommendations1 = self.content_based_methods.get_recommendations_positive_ratings_only_from_club_url_name(
            self.club.club_url_name)
        recommendations2 = self.content_based_methods.get_recommendations_from_positive_ratings(self.positive_ratings,
                                                                                                self.all_ratings)
        self.assertEqual(recommendations1, recommendations2)

    def test_get_recommendations_positive_ratings_only_from_club_url_name_wrong_club_url_name(self):
        self.set_up_content_based_methods_from_csv()
        recommendations = self.content_based_methods.get_recommendations_positive_ratings_only_from_club_url_name("-")
        self.assertEqual(recommendations, [])
