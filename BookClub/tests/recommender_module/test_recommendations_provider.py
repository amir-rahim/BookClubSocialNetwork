from django.test import TestCase, tag
from BookClub.models import User, Book, BookReview
from RecommenderModule import recommendations_provider
from RecommenderModule.recommenders.resources.item_based_collaborative_filtering_methods import ItemBasedCollaborativeFilteringMethods

@tag('recommenders')
class RecommendationsProviderTestCase(TestCase):

    fixtures = [
        'BookClub/tests/fixtures/default_users.json',
        'BookClub/tests/fixtures/default_books.json',
        'BookClub/tests/fixtures/default_book_reviews.json'
    ]

    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.book = Book.objects.get(pk=1)
        self.book_review = BookReview.objects.get(pk=1)

    def test_get_popularity_recommendations(self):
        recommendations = recommendations_provider.get_user_popularity_recommendations(self.user.username)
        self.assertEqual(len(recommendations), 10)
        self.assertEqual(type(recommendations[0]), str)

    def test_get_popularity_recommendations_does_not_contain_books_read_by_user(self):
        recommendations1 = recommendations_provider.get_user_popularity_recommendations(self.user.username)
        self.book.ISBN = recommendations1[0]
        self.book.save()
        self.assertTrue(self.book.ISBN in recommendations1)
        recommendations2 = recommendations_provider.get_user_popularity_recommendations(self.user.username)
        self.assertEqual(len(recommendations2), 10)
        self.assertFalse(self.book.ISBN in recommendations2)

    def test_get_personalised_recommendations(self):
        trainset = ItemBasedCollaborativeFilteringMethods().trainset
        books = []
        for book in trainset.all_items():
            books.append(trainset.to_raw_iid(book))
            if len(books) == 10:
                break
        book1 = Book.objects.create(title="Book 1", ISBN=books[0], author="John Doe", publicationYear="2002-02-02", publisher="Penguin")
        review1 = BookReview.objects.create(user=self.user, book=book1, rating=7)
        book2 = Book.objects.create(title="Book 2", ISBN=books[1], author="John Doe", publicationYear="2002-02-02", publisher="Penguin")
        review2 = BookReview.objects.create(user=self.user, book=book2, rating=8)
        personalised_recommendations = recommendations_provider.get_user_personalised_recommendations(self.user.username)
        self.assertEqual(len(personalised_recommendations), 10)
        self.assertEqual(type(personalised_recommendations[0]), str)

    def test_get_personalised_recommendations_does_not_contain_books_read_by_user(self):
        trainset = ItemBasedCollaborativeFilteringMethods().trainset
        books = []
        for book in trainset.all_items():
            books.append(trainset.to_raw_iid(book))
            if len(books) == 2:
                break
        book1 = Book.objects.create(title="Book 1", ISBN=books[0], author="John Doe", publicationYear="2002-02-02", publisher="Penguin")
        review1 = BookReview.objects.create(user=self.user, book=book1, rating=7)
        book2 = Book.objects.create(title="Book 2", ISBN=books[1], author="John Doe", publicationYear="2002-02-02", publisher="Penguin")
        review2 = BookReview.objects.create(user=self.user, book=book2, rating=8)
        personalised_recommendations1 = recommendations_provider.get_user_personalised_recommendations(self.user.username)
        book3 = Book.objects.create(title="Book 3", ISBN=personalised_recommendations1[0], author="John Doe", publicationYear="2002-02-02", publisher="Penguin")
        review3 = BookReview.objects.create(user=self.user, book=book3, rating=2)
        self.assertTrue(book3.ISBN in personalised_recommendations1)
        personalised_recommendations2 = recommendations_provider.get_user_personalised_recommendations(self.user.username)
        self.assertEqual(len(personalised_recommendations2), 10)
        self.assertFalse(book3.ISBN in personalised_recommendations2)

    def test_get_personalised_recommendations_wrong_user(self):
        recommendations = recommendations_provider.get_user_personalised_recommendations("X")
        self.assertEqual(len(recommendations), 0)
        self.assertEqual(recommendations, [])