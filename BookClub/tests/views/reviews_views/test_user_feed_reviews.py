from django.test import TestCase, tag
from django.urls import reverse

from BookClub.models import User, Book, BookReview

@tag('views', 'reviews', 'user_feed')
class UserFeedReviewListView(TestCase):

    fixtures = [
        'BookClub/tests/fixtures/real_books.json',
        'BookClub/tests/fixtures/default_users.json',
        'BookClub/tests/fixtures/default_books.json',
        'BookClub/tests/fixtures/default_book_reviews.json'
        ]

    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.url = reverse('personal_reviews')

    def test_user_feed_page_url(self):
        self.assertEqual(self.url, '/library/reviews/')

    def test_template_used(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'reviews/review_feed.html')

    def test_no_reviews(self):
        BookReview.objects.all().delete()
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        reviews = list(response.context['reviews'])
        self.assertEqual(len(reviews), 0)
        self.assertContains(response, 'There are no reviews, you can find books in the library <a href="/library/books/">here</a>.')

    def test_reviews_show(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        reviews = list(response.context['reviews'])
        self.assertEqual(len(reviews), 1)
        self.assertContains(response, 'Not too shabby')
        self.assertContains(response, 'Lorem Ipsum')
        self.assertContains(response, '1/10')

    def test_user_feed_context_data(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEquals(response.context['current_user'], self.user)