from django.test import TestCase, tag
from BookClub.models import User, Book, Club, ClubMembership
from RecommenderModule.recommenders.resources.library import Library
from RecommenderModule.recommenders.resources.data_provider import DataProvider
from collections import Counter

@tag('recommenders')
class LibraryTestCase(TestCase):

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
        self.club = Club.objects.get(pk=1)
        self.library_django = Library()

    """Initialise the variables to use the trainset-based library"""
    def set_up_library_trainset(self):
        data_provider = DataProvider(get_data_from_csv=True)
        trainset = data_provider.get_filtered_ratings_trainset()
        self.trainset = trainset
        for rating in trainset.all_ratings():
            self.user_trainset = trainset.to_raw_uid(rating[0])
            self.book_trainset = trainset.to_raw_iid(rating[1])
            self.rating_trainset = rating[2]
            break
        self.library_trainset = Library(trainset)

    def test_get_all_ratings_for_isbn_from_trainset(self):
        self.set_up_library_trainset()
        ratings = self.library_trainset.get_all_ratings_for_isbn_from_trainset(self.book_trainset)
        self.assertEqual(len(ratings), 60)

    def test_get_all_ratings_for_isbn_from_trainset_wrong_isbn(self):
        self.set_up_library_trainset()
        with self.assertRaises(ValueError):
            ratings = self.library_trainset.get_all_ratings_for_isbn_from_trainset("x")

    def test_get_all_books_rated_by_user_django(self):
        books = self.library_django.get_all_books_rated_by_user(self.user.username)
        self.assertEqual(len(books), 1)
        self.assertEqual(books[0], "0195153448")

    def test_get_all_books_rated_by_user_django_wrong_user_id(self):
        books = self.library_django.get_all_books_rated_by_user("x")
        self.assertEqual(books, [])
        self.assertEqual(len(books), 0)

    def test_get_all_books_rated_by_user_trainset(self):
        self.set_up_library_trainset()
        books = self.library_trainset.get_all_books_rated_by_user(self.user_trainset)
        self.assertEqual(type(books), type([]))
        self.assertTrue(self.book_trainset in books)

    def test_get_all_books_rated_by_user_trainset_wrong_user_id(self):
        self.set_up_library_trainset()
        books = self.library_django.get_all_books_rated_by_user("x")
        self.assertEqual(books, [])
        self.assertEqual(len(books), 0)

    def test_get_rating_from_user_and_book_django_right_user_right_book(self):
        rating = self.library_django.get_rating_from_user_and_book(self.user.username, self.book.ISBN)
        self.assertEqual(rating, 1)

    def test_get_rating_from_user_and_book_django_wrong_user(self):
        rating = self.library_django.get_rating_from_user_and_book("x", self.book.ISBN)
        self.assertEqual(rating, None)

    def test_get_rating_from_user_and_book_django_wrong_book(self):
        rating = self.library_django.get_rating_from_user_and_book(self.user.username, "x")
        self.assertEqual(rating, None)

    def test_get_rating_from_user_and_book_trainset_right_user_right_book(self):
        self.set_up_library_trainset()
        rating = self.library_trainset.get_rating_from_user_and_book(self.user_trainset, self.book_trainset)
        self.assertEqual(rating, self.rating_trainset)

    def test_get_rating_from_user_and_book_trainset_wrong_user(self):
        self.set_up_library_trainset()
        rating = self.library_trainset.get_rating_from_user_and_book("x", self.book_trainset)
        self.assertEqual(rating, None)

    def test_get_rating_from_user_and_book_trainset_wrong_book(self):
        self.set_up_library_trainset()
        rating = self.library_trainset.get_rating_from_user_and_book(self.user_trainset, "x")
        self.assertEqual(rating, None)

    def test_get_all_books_rated_by_club(self):
        books = self.library_django.get_all_books_rated_by_club(self.club.club_url_name)
        self.assertEqual(len(books), 3)
        club_memberships = ClubMembership.objects.filter(club=self.club)
        for membership in club_memberships:
            user = membership.user
            user_books = self.library_django.get_all_books_rated_by_user(user)
            for book in user_books:
                self.assertTrue(book in books)

    def test_get_all_books_rated_by_club_wrong_club(self):
        books = self.library_django.get_all_books_rated_by_club("-")
        self.assertEqual(books, [])

    def test_get_all_books_rated_by_club_can_contain_duplicates(self):
        books = self.library_django.get_all_books_rated_by_club(self.club.club_url_name)
        self.assertEqual(len(books), 3)
        counter = Counter(books)
        self.assertEqual(counter.get(self.book.ISBN), 2)
