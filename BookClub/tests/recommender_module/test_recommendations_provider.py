from django.test import TestCase, tag
from BookClub.models import User, Book, BookReview, Club
from RecommenderModule import recommendations_provider
from RecommenderModule.recommenders.resources.item_based_collaborative_filtering_methods import ItemBasedCollaborativeFilteringMethods
import joblib

@tag('recommenders')
class RecommendationsProviderTestCase(TestCase):

    fixtures = [
        'BookClub/tests/fixtures/default_users.json',
        'BookClub/tests/fixtures/default_books.json',
        'BookClub/tests/fixtures/default_book_reviews.json',
        'BookClub/tests/fixtures/default_clubs.json',
        'BookClub/tests/fixtures/default_club_members.json'
    ]

    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.book = Book.objects.get(pk=1)
        self.book_review = BookReview.objects.get(pk=1)
        self.club = Club.objects.get(pk=1)

    def test_get_user_popularity_recommendations(self):
        recommendations = recommendations_provider.get_user_popularity_recommendations(self.user.username)
        self.assertEqual(len(recommendations), 10)
        self.assertEqual(type(recommendations[0]), str)

    def test_get_user_popularity_recommendations_does_not_contain_books_read_by_user(self):
        recommendations1 = recommendations_provider.get_user_popularity_recommendations(self.user.username)
        self.book.ISBN = recommendations1[0]
        self.book.save()
        self.assertTrue(self.book.ISBN in recommendations1)
        recommendations2 = recommendations_provider.get_user_popularity_recommendations(self.user.username)
        self.assertEqual(len(recommendations2), 10)
        self.assertFalse(self.book.ISBN in recommendations2)

    def test_get_user_popularity_recommendations_wrong_user_id(self):
        recommendations = recommendations_provider.get_user_popularity_recommendations("X")
        self.assertEqual(len(recommendations), 10)
        self.assertEqual(type(recommendations[0]), str)

    def test_get_user_personalised_recommendations(self):
        trainset = ItemBasedCollaborativeFilteringMethods().trainset
        i = 0
        for book in trainset.all_items():
            book_isbn = trainset.to_raw_iid(book)
            book1 = Book.objects.create(title=f"Book {i}", ISBN=book_isbn, author="John Doe",
                                        publicationYear="2002-02-02", publisher="Penguin")
            review1 = BookReview.objects.create(creator=self.user, book=book1, book_rating=7)
            i += 1
            if i >= 10:
                break
        personalised_recommendations = recommendations_provider.get_user_personalised_recommendations(self.user.username)
        self.assertEqual(len(personalised_recommendations), 10)
        self.assertEqual(type(personalised_recommendations[0]), str)

    def test_get_user_personalised_recommendations_does_not_contain_books_read_by_user(self):
        trainset = ItemBasedCollaborativeFilteringMethods().trainset
        i = 0
        for book in trainset.all_items():
            book_isbn = trainset.to_raw_iid(book)
            book1 = Book.objects.create(title=f"Book {i}", ISBN=book_isbn, author="John Doe",
                                        publicationYear="2002-02-02", publisher="Penguin")
            review1 = BookReview.objects.create(creator=self.user, book=book1, book_rating=7)
            i += 1
            if i >= 10:
                break
        personalised_recommendations1 = recommendations_provider.get_user_personalised_recommendations(self.user.username)
        book2 = Book.objects.create(title="Book 3", ISBN=personalised_recommendations1[0], author="John Doe", publicationYear="2002-02-02", publisher="Penguin")
        review2 = BookReview.objects.create(creator=self.user, book=book2, book_rating=2)
        self.assertTrue(book2.ISBN in personalised_recommendations1)
        personalised_recommendations2 = recommendations_provider.get_user_personalised_recommendations(self.user.username)
        self.assertEqual(len(personalised_recommendations2), 10)
        self.assertFalse(book2.ISBN in personalised_recommendations2)

    def test_get_user_personalised_recommendations_wrong_user_id(self):
        recommendations = recommendations_provider.get_user_personalised_recommendations("X")
        self.assertEqual(recommendations, [])

    def test_get_club_popularity_recommendations(self):
        recommendations = recommendations_provider.get_club_popularity_recommendations(self.club.club_url_name)
        self.assertEqual(len(recommendations), 10)
        self.assertEqual(type(recommendations[0]), str)

    def test_get_club_popularity_recommendations_does_not_contain_books_read_by_members(self):
        recommendations1 = recommendations_provider.get_club_popularity_recommendations(self.club.club_url_name)
        self.book.ISBN = recommendations1[0]
        self.book.save()
        self.assertTrue(self.book.ISBN in recommendations1)
        recommendations2 = recommendations_provider.get_club_popularity_recommendations(self.club.club_url_name)
        self.assertEqual(len(recommendations2), 10)
        self.assertFalse(self.book.ISBN in recommendations2)

    def test_get_club_popularity_recommendations_wrong_club_url_name(self):
        recommendations = recommendations_provider.get_club_popularity_recommendations("-")
        self.assertEqual(len(recommendations), 10)
        self.assertEqual(type(recommendations[0]), str)

    def test_get_club_personalised_recommendations(self):
        trainset = ItemBasedCollaborativeFilteringMethods().trainset
        i = 0
        for book in trainset.all_items():
            book_isbn = trainset.to_raw_iid(book)
            book1 = Book.objects.create(title=f"Book {i}", ISBN=book_isbn, author="John Doe",
                                        publicationYear="2002-02-02", publisher="Penguin")
            review1 = BookReview.objects.create(creator=self.user, book=book1, book_rating=7)
            i += 1
            if i >= 10:
                break
        personalised_recommendations = recommendations_provider.get_club_personalised_recommendations(self.club.club_url_name)
        self.assertEqual(len(personalised_recommendations), 10)
        self.assertEqual(type(personalised_recommendations[0]), str)

    def test_get_club_personalised_recommendations_does_not_contain_books_read_by_members(self):
        trainset = ItemBasedCollaborativeFilteringMethods().trainset
        i = 0
        for book in trainset.all_items():
            book_isbn = trainset.to_raw_iid(book)
            book1 = Book.objects.create(title=f"Book {i}", ISBN=book_isbn, author="John Doe", publicationYear="2002-02-02", publisher="Penguin")
            review1 = BookReview.objects.create(creator=self.user, book=book1, book_rating=7)
            i += 1
            if i >= 10:
                break
        personalised_recommendations1 = recommendations_provider.get_club_personalised_recommendations(self.club.club_url_name)
        book2 = Book.objects.create(title="Book 3", ISBN=personalised_recommendations1[0], author="John Doe", publicationYear="2002-02-02", publisher="Penguin")
        review2 = BookReview.objects.create(creator=self.user, book=book2, book_rating=2)
        self.assertTrue(book2.ISBN in personalised_recommendations1)
        personalised_recommendations2 = recommendations_provider.get_club_personalised_recommendations(self.club.club_url_name)
        self.assertEqual(len(personalised_recommendations2), 10)
        self.assertFalse(book2.ISBN in personalised_recommendations2)

    def test_get_club_personalised_recommendations_wrong_club_url_name(self):
        recommendations = recommendations_provider.get_club_personalised_recommendations("-")
        self.assertEqual(recommendations, [])

    def test_get_list_of_all_books_in_item_based_trainset(self):
        books1 = recommendations_provider.get_list_of_all_books_in_item_based_trainset()
        self.assertFalse(books1 is None)
        self.assertNotEqual(books1, [])
        path_to_item_based_trainset = "RecommenderModule/recommenders/resources/item_based_model/trainset.sav"
        trainset = joblib.load(path_to_item_based_trainset)
        books2 = []
        for inner_id in trainset.all_items():
            books2.append(trainset.to_raw_iid(inner_id))
        self.assertEqual(books1, books2)
