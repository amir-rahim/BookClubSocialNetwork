from django.test import TestCase, tag
from RecommenderModule.recommenders.resources.item_based_collaborative_filtering_methods import ItemBasedCollaborativeFilteringMethods
from RecommenderModule.recommenders.resources.data_provider import DataProvider
from RecommenderModule.recommenders.resources.library import Library

@tag('recommenders')
class ItemBasedRecommenderMethodsTestCase(TestCase):

    def setUp(self):
        data_provider = DataProvider(get_data_from_csv=True)
        self.trainset = data_provider.get_filtered_ratings_trainset()
        self.item_based_methods = ItemBasedCollaborativeFilteringMethods(trainset=self.trainset, print_status=False)
        self.user_id = self.trainset.to_raw_uid(4)
        self.library = Library(trainset=self.trainset)

    def test_get_trainset_user_book_ratings_with_items_parameter(self):
        user_books = self.library.get_all_books_rated_by_user(self.user_id)
        self.assertEqual(len(user_books), 5)
        inner_items = self.item_based_methods.get_trainset_user_book_ratings(self.user_id, items=user_books)
        self.assertEqual(len(user_books), len(inner_items))
        for inner_item, rating in inner_items:
            raw_item_id = self.trainset.to_raw_iid(inner_item)
            self.assertTrue(raw_item_id in user_books)

    def test_get_trainset_user_book_ratings_without_items_parameter(self):
        user_books = self.library.get_all_books_rated_by_user(self.user_id)
        inner_items = self.item_based_methods.get_trainset_user_book_ratings(self.user_id)
        self.assertEqual(len(user_books), 5)
        self.assertEqual(len(user_books), len(inner_items))
        for inner_item, rating in inner_items:
            raw_item_id = self.trainset.to_raw_iid(inner_item)
            self.assertTrue(raw_item_id in user_books)

    def test_get_trainset_user_book_ratings_wrong_user(self):
        inner_items = self.item_based_methods.get_trainset_user_book_ratings("X")
        self.assertEqual(inner_items, [])

    def test_get_trainset_user_book_ratings_with_min_rating_parameter(self):
        min_rating = 6
        inner_items = self.item_based_methods.get_trainset_user_book_ratings(self.user_id, min_rating=min_rating)
        self.assertEqual(len(inner_items), 3)
        for inner_item, rating in inner_items:
            self.assertTrue(rating >= min_rating)

    def test_get_recommendations_from_user_inner_ratings_all_ratings(self):
        all_ratings = self.item_based_methods.get_trainset_user_book_ratings(self.user_id)
        recommendations = self.item_based_methods.get_recommendations_from_user_inner_ratings(ratings=all_ratings)
        self.assertEqual(len(recommendations), 10)
        self.assertEqual(type(recommendations[0]), str)
        for inner_item, rating in all_ratings:
            self.assertFalse(self.trainset.to_raw_iid(inner_item) in recommendations)

    def test_get_recommendations_from_user_inner_ratings_positive_ratings_only(self):
        all_ratings = self.item_based_methods.get_trainset_user_book_ratings(self.user_id)
        positive_ratings = self.item_based_methods.get_trainset_user_book_ratings(self.user_id, min_rating=6)
        recommendations = self.item_based_methods.get_recommendations_from_user_inner_ratings(ratings=positive_ratings, all_books_rated=all_ratings)
        self.assertEqual(len(recommendations), 10)
        self.assertEqual(type(recommendations[0]), str)
        for inner_item, rating in all_ratings:
            self.assertFalse(self.trainset.to_raw_iid(inner_item) in recommendations)

    def test_get_recommendations_all_ratings_from_user_id(self):
        recommendations1 = self.item_based_methods.get_recommendations_all_ratings_from_user_id(self.user_id)
        all_ratings = self.item_based_methods.get_trainset_user_book_ratings(self.user_id)
        recommendations2 = self.item_based_methods.get_recommendations_from_user_inner_ratings(ratings=all_ratings)
        self.assertEqual(recommendations1, recommendations2)

    def test_get_recommendations_positive_ratings_only_from_user_id(self):
        recommendations1 = self.item_based_methods.get_recommendations_positive_ratings_only_from_user_id(self.user_id)
        all_ratings = self.item_based_methods.get_trainset_user_book_ratings(self.user_id)
        positive_ratings = self.item_based_methods.get_trainset_user_book_ratings(self.user_id, min_rating=6)
        recommendations2 = self.item_based_methods.get_recommendations_from_user_inner_ratings(ratings=positive_ratings, all_books_rated=all_ratings)
        self.assertEqual(recommendations1, recommendations2)