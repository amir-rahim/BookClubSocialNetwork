import numpy as np
from django.test import TestCase, tag
from RecommenderModule.recommenders.resources.popular_books_recommender_methods import PopularBooksMethods
from RecommenderModule.recommenders.resources.data_provider import DataProvider
import math

@tag('recommenders')
class PopularBooksRecommenderMethodsTestCase(TestCase):

    def setUp(self):
        data_provider = DataProvider(get_data_from_csv=True)
        self.trainset = data_provider.get_filtered_ratings_trainset()
        self.popular_books_methods = PopularBooksMethods(print_status=False, trainset=self.trainset)
        self.book_id = self.trainset.to_raw_iid(1)

    def test_get_average_rating(self):
        average_rating = self.popular_books_methods.get_average_rating(self.book_id)
        sum = 0
        for user_id, rating in self.trainset.ir[1]:
            sum += rating
        self.assertEqual(average_rating, sum/len(self.trainset.ir[1]))

    def test_compute_sorted_average_ratings(self):
        average_ratings_list = self.popular_books_methods.sorted_average_ratings
        i = 0
        for book, score in average_ratings_list:
            average_rating = self.popular_books_methods.get_average_rating(book)
            self.assertEqual(score, average_rating)
            if i > 0:
                self.assertTrue(average_ratings_list[i - 1][1] >= score)
            i += 1

    def test_get_median_rating(self):
        median_rating = self.popular_books_methods.get_median_rating(self.book_id)
        all_ratings = [pair[1] for pair in self.trainset.ir[1]]
        all_ratings_sorted = np.sort(all_ratings)
        if len(all_ratings_sorted) % 2 == 0:
            index = (len(all_ratings_sorted) // 2) - 1
            calculated_median = (all_ratings_sorted[index] + all_ratings_sorted[index + 1]) / 2
        else: # odd number of ratings
            index = (len(all_ratings_sorted) // 2)
            calculated_median = all_ratings_sorted[index]
        self.assertEqual(median_rating, calculated_median)

    def test_compute_sorted_median_ratings(self):
        median_ratings_list = self.popular_books_methods.sorted_median_ratings
        i = 0
        for book, score in median_ratings_list:
            median_rating = self.popular_books_methods.get_median_rating(book)
            self.assertEqual(score, median_rating)
            if i > 0:
                self.assertTrue(median_ratings_list[i - 1][1] >= score)
            i += 1

    def test_compute_sorted_combination_scores(self):
        combination_scores_list = self.popular_books_methods.sorted_combination_scores
        i = 0
        for book, score in combination_scores_list:
            average_rating = self.popular_books_methods.get_average_rating(book)
            median_rating = self.popular_books_methods.get_median_rating(book)
            self.assertEqual(score, math.sqrt(average_rating * median_rating))
            if i > 0:
                self.assertTrue(combination_scores_list[i-1][1] >= score)
            i += 1

    def test_get_recommendations_from_average_no_user_read_books(self):
        average_recommendations = self.popular_books_methods.get_recommendations_from_average()
        average_popularity_list = [pair[0] for pair in self.popular_books_methods.sorted_average_ratings]
        self.assertEqual(len(average_recommendations), 10)
        for i in range(len(average_recommendations)):
            self.assertEqual(average_recommendations[i], average_popularity_list[i])

    def test_get_recommendations_from_average_does_not_contain_books_read_by_user(self):
        average_recommendations_1 = self.popular_books_methods.get_recommendations_from_average()
        user_read_books = [average_recommendations_1[0], average_recommendations_1[1]]
        self.assertTrue(user_read_books[0] in average_recommendations_1)
        self.assertTrue(user_read_books[1] in average_recommendations_1)
        average_recommendations_2 = self.popular_books_methods.get_recommendations_from_average(user_read_books=user_read_books)
        self.assertEqual(len(average_recommendations_2), 10)
        self.assertFalse(user_read_books[0] in average_recommendations_2)
        self.assertFalse(user_read_books[1] in average_recommendations_2)

    def test_get_recommendations_from_median_no_user_read_books(self):
        median_recommendations = self.popular_books_methods.get_recommendations_from_median()
        median_popularity_list = [pair[0] for pair in self.popular_books_methods.sorted_median_ratings]
        self.assertEqual(len(median_recommendations), 10)
        for i in range(len(median_recommendations)):
            self.assertEqual(median_recommendations[i], median_popularity_list[i])

    def test_get_recommendations_from_median_does_not_contain_books_read_by_user(self):
        median_recommendations_1 = self.popular_books_methods.get_recommendations_from_median()
        user_read_books = [median_recommendations_1[0], median_recommendations_1[1]]
        self.assertTrue(user_read_books[0] in median_recommendations_1)
        self.assertTrue(user_read_books[1] in median_recommendations_1)
        median_recommendations_2 = self.popular_books_methods.get_recommendations_from_median(user_read_books=user_read_books)
        self.assertEqual(len(median_recommendations_2), 10)
        self.assertFalse(user_read_books[0] in median_recommendations_2)
        self.assertFalse(user_read_books[1] in median_recommendations_2)

    def test_get_recommendations_from_average_and_median_no_user_read_books(self):
        combination_recommendations = self.popular_books_methods.get_recommendations_from_average_and_median()
        combination_popularity_list = [pair[0] for pair in self.popular_books_methods.sorted_combination_scores]
        self.assertEqual(len(combination_recommendations), 10)
        for i in range(len(combination_recommendations)):
            self.assertEqual(combination_recommendations[i], combination_popularity_list[i])

    def test_get_recommendations_from_average_and_median_does_not_contain_books_read_by_user(self):
        combination_recommendations_1 = self.popular_books_methods.get_recommendations_from_average_and_median()
        user_read_books = [combination_recommendations_1[0], combination_recommendations_1[1]]
        self.assertTrue(user_read_books[0] in combination_recommendations_1)
        self.assertTrue(user_read_books[1] in combination_recommendations_1)
        combination_recommendations_2 = self.popular_books_methods.get_recommendations_from_average_and_median(user_read_books=user_read_books)
        self.assertEqual(len(combination_recommendations_2), 10)
        self.assertFalse(user_read_books[0] in combination_recommendations_2)
        self.assertFalse(user_read_books[1] in combination_recommendations_2)
