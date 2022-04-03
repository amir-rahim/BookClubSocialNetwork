"""Unit testing of the Create Review view"""
from datetime import date

from django.test import TestCase, tag
from django.urls import reverse

from BookClub.forms import ReviewForm
from BookClub.models import Book, BookReview, User
from BookClub.tests.helpers import reverse_with_next


@tag('views', 'review', 'create_review')
class CreateReviewViewTestcase(TestCase):
    """Tests for the Create Review view"""
    fixtures = [
        "BookClub/tests/fixtures/default_users.json",
        "BookClub/tests/fixtures/default_books.json",
        "BookClub/tests/fixtures/default_book_reviews.json"
    ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.user = User.objects.get(username='jackdoe')
        self.book = Book.objects.get(pk=1)
        self.url = reverse('create_review', kwargs={'book_id': self.book.pk})
        self.data = {
            'book_rating': 7,
            'title':'Book Title',
            'content': 'A pretty good book'
        }

    def test_create_review_url(self):
        self.assertEqual(self.url, '/library/books/1/create/')

    def test_redirect_non_existing_id(self):
        self.client.login(username=self.user.username, password="Password123")
        url = reverse('create_review', kwargs={'book_id': 555})
        redirect_url = reverse('library_books')
        response = self.client.post(url, self.data, follow=True)
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200, fetch_redirect_response=True
                             )

    def test_post_create_review_redirects_when_not_logged_in(self):
        review_count_before = BookReview.objects.count()
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.post(self.url, self.data, follow=True)
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200, fetch_redirect_response=True
                             )
        self.assertTemplateUsed(response, 'authentication/login.html')
        review_count_after = BookReview.objects.count()
        self.assertEqual(review_count_after, review_count_before)

    def test_get_create_review_redirects_when_not_logged_in(self):
        review_count_before = BookReview.objects.count()
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.post(self.url, follow=True)
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200, fetch_redirect_response=True
                             )
        self.assertTemplateUsed(response, 'authentication/login.html')
        review_count_after = BookReview.objects.count()
        self.assertEqual(review_count_after, review_count_before)

    def test_get_create_review(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reviews/create_review.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, ReviewForm))
        self.assertFalse(form.is_bound)

    def test_unsuccessful_review_existing(self):
        existing_review = BookReview.objects.all()[0]
        existing_review_book = existing_review.book
        existing_review_user = existing_review.creator
        url_to_recreate_existing_review = reverse('create_review', kwargs={'book_id': existing_review_book.pk})

        self.client.login(username=existing_review_user.username, password='Password123')
        before_count = BookReview.objects.count()
        response = self.client.post(url_to_recreate_existing_review, self.data)
        after_count = BookReview.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 302)

    def test_unsuccessful_review_invalid_form(self):
        self.data['content'] = 'x' * 1025
        self.client.login(username=self.user.username, password='Password123')
        before_count = BookReview.objects.count()
        saving_date = date.today()
        response = self.client.post(self.url, self.data, follow=True)
        after_count = BookReview.objects.count()
        self.assertEqual(after_count, before_count)

    def test_successful_create_review(self):
        self.client.login(username=self.user.username, password='Password123')
        before_count = BookReview.objects.count()
        saving_date = date.today()
        response = self.client.post(self.url, self.data, follow=True)
        review = BookReview.objects.get(book=self.book, creator=self.user)
        after_count = BookReview.objects.count()
        self.assertEqual(after_count, before_count+1)
        response_url = reverse('book_reviews', kwargs={'book_id': self.book.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'library/book_reviews.html')
        self.assertEqual(review.book_rating, self.data['book_rating'])
        self.assertEqual(review.content, self.data['content'])
        self.assertEqual(review.title,self.data['title'])
        self.assertEqual(review.created_on.date(), saving_date)
