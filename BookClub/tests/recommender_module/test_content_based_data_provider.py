from django.test import TestCase, tag
from RecommenderModule.recommenders.resources.content_based_data_provider import ContentBasedDataProvider
from RecommenderModule.recommenders.resources.data_provider import DataProvider
from surprise import Dataset, Reader

@tag('recommenders')
class ContentBasedDataProviderTestCase(TestCase):

    fixtures = [
        'BookClub/tests/fixtures/default_content_based_books.json'
    ]

    def set_up_csv_content_based_data_provider(self):
        self.content_based_data_provider = ContentBasedDataProvider(get_data_from_csv=True)

    def set_up_django_content_based_data_provider(self):
        self.content_based_data_provider = ContentBasedDataProvider(get_data_from_csv=False)


    def test_compute_filtered_book_depository_dataset_csv(self):
        self.set_up_csv_content_based_data_provider()
        filtered_book_depository_dataset = self.content_based_data_provider.filtered_book_depository_dataset
        self.assertEqual(len(filtered_book_depository_dataset), 3909)
        columns = ['authors', 'bestsellers-rank', 'categories', 'description', 'dimension-x', 'dimension-y', 'dimension-z', 'edition', 'edition-statement', 'for-ages', 'format', 'id', 'illustrations-note', 'image-checksum', 'image-path', 'image-url', 'imprint', 'index-date', 'isbn10', 'isbn13', 'lang', 'publication-date', 'publication-place', 'rating-avg', 'rating-count', 'title', 'url', 'weight']
        self.assertEqual(list(filtered_book_depository_dataset.columns), columns)

    def test_compute_filtered_book_depository_dataset_django(self):
        self.set_up_django_content_based_data_provider()
        filtered_book_depository_dataset = self.content_based_data_provider.filtered_book_depository_dataset
        self.assertEqual(len(filtered_book_depository_dataset), 3)
        columns = ['authors', 'bestsellers-rank', 'categories', 'description', 'dimension-x', 'dimension-y', 'dimension-z', 'edition', 'edition-statement', 'for-ages', 'format', 'id', 'illustrations-note', 'image-checksum', 'image-path', 'image-url', 'imprint', 'index-date', 'isbn10', 'isbn13', 'lang', 'publication-date', 'publication-place', 'rating-avg', 'rating-count', 'title', 'url', 'weight']
        self.assertEqual(list(filtered_book_depository_dataset.columns), columns)

    def test_make_list_of_dict_book_content_csv(self):
        self.set_up_csv_content_based_data_provider()
        book_content_list = self.content_based_data_provider.book_content_list
        self.assertEqual(len(book_content_list), 3901)
        for book_content in book_content_list:
            self.assertEqual(list(book_content.keys()), ["book_isbn", "categories", "publication_year"])
            self.assertEqual(type(book_content["book_isbn"]), str)
            self.assertEqual(type(book_content["categories"]), list)
            self.assertEqual(type(book_content["publication_year"]), int)

    def test_make_list_of_dict_book_content_django(self):
        self.set_up_django_content_based_data_provider()
        book_content_list = self.content_based_data_provider.book_content_list
        self.assertEqual(len(book_content_list), 3)
        for book_content in book_content_list:
            self.assertEqual(list(book_content.keys()), ["book_isbn", "categories", "publication_year"])
            self.assertEqual(type(book_content["book_isbn"]), str)
            self.assertEqual(type(book_content["categories"]), list)
            self.assertEqual(type(book_content["publication_year"]), int)


    def test_get_list_of_dict_book_content_csv(self):
        self.set_up_csv_content_based_data_provider()
        book_content_list = self.content_based_data_provider.get_list_of_dict_book_content()
        self.assertEqual(len(book_content_list), 3901)
        for book_content in book_content_list:
            self.assertEqual(list(book_content.keys()), ["book_isbn", "categories", "publication_year"])
            self.assertEqual(type(book_content["book_isbn"]), str)
            self.assertEqual(type(book_content["categories"]), list)
            self.assertEqual(type(book_content["publication_year"]), int)

    def test_get_list_of_dict_book_content_django(self):
        self.set_up_django_content_based_data_provider()
        book_content_list = self.content_based_data_provider.get_list_of_dict_book_content()
        self.assertEqual(len(book_content_list), 3)
        for book_content in book_content_list:
            self.assertEqual(list(book_content.keys()), ["book_isbn", "categories", "publication_year"])
            self.assertEqual(type(book_content["book_isbn"]), str)
            self.assertEqual(type(book_content["categories"]), list)
            self.assertEqual(type(book_content["publication_year"]), int)

    def test_get_all_books_in_trainset(self):
        content_based_data_provider = ContentBasedDataProvider()
        data_provider = DataProvider(get_data_from_csv=True, filtering_min_ratings_threshold=100)
        ratings_df = data_provider.filtered_ratings_df
        reader = Reader(line_format='user item rating', sep=';', skip_lines=0, rating_scale=(0, 10))
        ratings_dataset = Dataset.load_from_df(ratings_df, reader)
        original_trainset = ratings_dataset.build_full_trainset()
        all_books_1 = content_based_data_provider.get_all_books_in_trainset(original_trainset)
        all_books_2 = []
        for index, row in ratings_df.iterrows():
            book_isbn = row["ISBN"]
            if book_isbn not in all_books_2:
                all_books_2.append(book_isbn)
        self.assertEqual(len(all_books_1), len(all_books_2))
        for book in all_books_1:
            self.assertTrue(book in all_books_2)