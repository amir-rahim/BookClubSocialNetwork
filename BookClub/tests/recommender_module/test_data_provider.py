import pandas as pd
from django.test import TestCase, tag
from RecommenderModule.recommenders.resources.data_provider import DataProvider
from surprise.dataset import DatasetAutoFolds
from surprise import Trainset

@tag('recommenders')
class DataProviderTestCase(TestCase):

    fixtures = [
        'BookClub/tests/fixtures/default_users.json',
        'BookClub/tests/fixtures/default_books.json',
        'BookClub/tests/fixtures/default_book_reviews.json'
    ]

    def setUp(self):
        self.data_provider = DataProvider()
        self.data_provider_csv = DataProvider(get_data_from_csv=True)

    def test_get_ratings_from_django_database(self):
        self.data_provider.get_ratings_from_django_database()
        ratings_df = self.data_provider.ratings_df
        self.assertEqual(type(ratings_df), pd.DataFrame)
        self.assertEqual(len(ratings_df), 2)
        rating1 = ratings_df.iloc[0]
        self.assertEqual(rating1["User-ID"], "johndoe")
        self.assertEqual(rating1["ISBN"], "0195153448")
        self.assertEqual(rating1["Book-Rating"], 1)
        rating2 = ratings_df.iloc[1]
        self.assertEqual(rating2["User-ID"], "amirdoe")
        self.assertEqual(rating2["ISBN"], "0195153448")
        self.assertEqual(rating2["Book-Rating"], 1)

    def test_get_filtered_books_list(self):
        filtered_books_list = self.data_provider_csv.get_filtered_books_list()
        ratings_df = self.data_provider_csv.ratings_df
        ratings_counts = ratings_df["ISBN"].value_counts()
        min_ratings_threshold = self.data_provider_csv.filtering_min_ratings_threshold
        for isbn in ratings_counts.keys():
            if ratings_counts[isbn] >= min_ratings_threshold:
                self.assertTrue(isbn in filtered_books_list)
            else:
                self.assertFalse(isbn in filtered_books_list)

    def test_get_filtered_ratings_dataset(self):
        filtered_ratings_dataset = self.data_provider_csv.get_filtered_ratings_dataset()
        self.assertEqual(type(filtered_ratings_dataset), DatasetAutoFolds)
        filtered_books_list = self.data_provider_csv.get_filtered_books_list()
        filtered_books_list_from_dataset = []
        for rating in filtered_ratings_dataset.raw_ratings:
            isbn = rating[1]
            self.assertTrue(isbn in filtered_books_list)
            if isbn not in filtered_books_list_from_dataset:
                filtered_books_list_from_dataset.append(isbn)
        self.assertEqual(len(filtered_books_list), len(filtered_books_list_from_dataset))
        ratings_df = self.data_provider_csv.ratings_df
        filtered_ratings_count = 0
        for index, rating in ratings_df.iterrows():
            if rating["ISBN"] in filtered_books_list:
                filtered_ratings_count += 1
        self.assertEqual(len(filtered_ratings_dataset.raw_ratings), filtered_ratings_count)

    def test_get_filtered_ratings_trainset(self):
        filtered_ratings_trainset = self.data_provider_csv.get_filtered_ratings_trainset()
        self.assertEqual(type(filtered_ratings_trainset), Trainset)
        filtered_books_list = self.data_provider_csv.get_filtered_books_list()
        self.assertEqual(filtered_ratings_trainset.n_items, len(filtered_books_list))
        filtered_ratings_dataset = self.data_provider_csv.get_filtered_ratings_dataset()
        self.assertEqual(filtered_ratings_trainset.n_ratings, len(filtered_ratings_dataset.raw_ratings))