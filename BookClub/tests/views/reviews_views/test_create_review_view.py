from datetime import date

from django.test import TestCase, tag
from django.urls import reverse

from BookClub.models.user import User
from BookClub.models.book import Book
from BookClub.models.review import BookReview

from BookClub.forms.review import ReviewForm

from BookClub.tests.helpers import reverse_with_next


@tag('create_review', 'review', 'reviewform', 'book', 'user')
class CreateReviewViewTestcase(TestCase):
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
            'rating': 7,
            'review': 'A pretty good book'
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
        self.assertTemplateUsed(response, 'login.html')
        review_count_after = BookReview.objects.count()
        self.assertEqual(review_count_after, review_count_before)

    def test_get_create_review_redirects_when_not_logged_in(self):
        review_count_before = BookReview.objects.count()
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.post(self.url, follow=True)
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200, fetch_redirect_response=True
                             )
        self.assertTemplateUsed(response, 'login.html')
        review_count_after = BookReview.objects.count()
        self.assertEqual(review_count_after, review_count_before)

    def test_get_create_review(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_review.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, ReviewForm))
        self.assertFalse(form.is_bound)

    def test_unsuccessful_review_existing(self):
        existing_review = BookReview.objects.all()[0]
        existing_review_book = existing_review.book
        existing_review_user = existing_review.user
        url_to_recreate_existing_review = reverse('create_review', kwargs={'book_id': existing_review_book.pk})

        self.client.login(username=existing_review_user.username, password='Password123')
        before_count = BookReview.objects.count()
        response = self.client.post(url_to_recreate_existing_review, self.data)
        after_count = BookReview.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 302)

    def test_unsuccessful_review_invalid_form(self):
        self.data['review'] = 'x' * 1025
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
        review = BookReview.objects.get(book=self.book, user=self.user)
        after_count = BookReview.objects.count()
        self.assertEqual(after_count, before_count+1)
        response_url = reverse('book_reviews', kwargs={'book_id': self.book.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'book_reviews.html')
        self.assertEqual(review.rating, self.data['rating'])
        self.assertEqual(review.review, self.data['review'])
        self.assertEqual(review.createdOn.year, saving_date.year)
        self.assertEqual(review.createdOn.month, saving_date.month)
        self.assertEqual(review.createdOn.day, saving_date.day)
