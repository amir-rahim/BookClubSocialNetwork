from django.test import TestCase, tag
from BookClub.models import User, Book, BookReview
from BookClub.recommender_module import recommendations_provider

@tag('recommenders')
class RecommendersTestCase(TestCase):

    fixtures = [
        'BookClub/tests/fixtures/default_users.json',
        'BookClub/tests/fixtures/default_books.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='johndoe')


    def test_get_popularity_recommendations(self):
        recommendations = recommendations_provider.get_popularity_recommendations(self.user)
        self.assertEqual(len(recommendations), 10)
        self.assertTrue(all(isinstance(isbn, str) for isbn in recommendations))

    def test_get_popularity_recommendations_exclude_books_read(self):
        first_recommendations = recommendations_provider.get_popularity_recommendations(self.user)
        isbn1 = first_recommendations[0]
        Book.objects.filter(pk=1).update(ISBN=isbn1)
        book1 = Book.objects.get(pk=1)
        review1 = BookReview.objects.create(book = book1, user = self.user, rating = 4)
        isbn2 = first_recommendations[1]
        Book.objects.filter(pk=2).update(ISBN=isbn2)
        book2 = Book.objects.get(pk=2)
        review2 = BookReview.objects.create(book = book2, user = self.user, rating = 7)
        second_recommendations = recommendations_provider.get_popularity_recommendations(self.user)
        books_read_by_user = recommendations_provider.get_user_read_books(self.user)
        self.assertEqual(len(books_read_by_user), 2)
        self.assertTrue(isbn1 in books_read_by_user)
        self.assertTrue(isbn2 in books_read_by_user)
        self.assertTrue(isbn1 in first_recommendations)
        self.assertTrue(isbn2 in first_recommendations)
        self.assertFalse(isbn1 in second_recommendations)
        self.assertFalse(isbn2 in second_recommendations)


    def test_get_books_read_by_user(self):
        book1 = Book.objects.get(pk=1)
        review1 = BookReview.objects.create(book = book1, user = self.user, rating = 4)
        book2 = Book.objects.get(pk=2)
        review2 = BookReview.objects.create(book = book2, user = self.user, rating = 7)
        books_read_by_user = recommendations_provider.get_user_read_books(self.user)
        self.assertEqual(len(books_read_by_user), 2)
        self.assertEqual(books_read_by_user[0], book1.ISBN)
        self.assertEqual(books_read_by_user[1], book2.ISBN)

    def test_get_books_read_by_user_no_book(self):
        user_read_books = recommendations_provider.get_user_read_books(self.user)
        self.assertEqual(user_read_books, [])
