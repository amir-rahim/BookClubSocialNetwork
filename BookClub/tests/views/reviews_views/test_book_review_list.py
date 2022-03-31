from django.test import TestCase, tag
from django.urls import reverse

from BookClub.models import User, Book, BookReview


@tag('book_review', 'review_list')
class BookReviewListView(TestCase):

    fixtures = [
        'BookClub/tests/fixtures/real_books.json',
        'BookClub/tests/fixtures/default_users.json',
        'BookClub/tests/fixtures/default_books.json',
        'BookClub/tests/fixtures/default_book_reviews.json'
        ]

    def setUp(self):
        self.book = Book.objects.get(pk=54273)
        self.book_with_reviews = Book.objects.get(pk=1)
        self.user1 = User.objects.get(pk=1)
        self.user2 = User.objects.get(pk=2)
        self.user3 = User.objects.get(pk=3)
        self.user4 = User.objects.get(pk=4)
        self.url = reverse('book_reviews', kwargs={'book_id' : 54273})
        self.url_with_reviews = reverse('book_reviews', kwargs={'book_id' : 1})

    def test_url(self):
        self.assertEquals(self.url, "/library/books/"+str(54273)+"/reviews/")

    def test_no_reviews_returns_empty(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'library/book_reviews.html')
        context = response.context
        self.assertEqual(len(context.get('reviews')), 0)
        self.assertContains(response, "No reviews")

    def test_view_returns_all_views(self):
        response = self.client.get(self.url_with_reviews)
        reviews = BookReview.objects.filter(book=self.book_with_reviews)
        returned_reviews = response.context.get('reviews')
        for review in reviews:
            self.assertIn(review, returned_reviews)
