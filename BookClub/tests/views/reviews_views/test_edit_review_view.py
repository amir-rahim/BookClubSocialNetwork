"""Tests for editing review and rating"""
from django.test import TestCase, tag
from django.urls import reverse
from BookClub.models import User, Book, BookReview
from BookClub.tests.helpers import LogInTester, reverse_with_next
from django.contrib import messages
from django.contrib.messages import get_messages


@tag('book', 'editreview','review')
class EditReviewView(TestCase, LogInTester):
    """Tests for editing review and rating"""

    fixtures = [
        'BookClub/tests/fixtures/default_books.json',
        'BookClub/tests/fixtures/default_users.json',
        'BookClub/tests/fixtures/default_book_reviews.json',
    ]

    def setUp(self):
        self.book = Book.objects.get(pk=1)
        self.user = User.objects.get(pk=1)
        self.another_user = User.objects.get(pk=2)
        self.book_review = BookReview.objects.get(pk=1)
        self.data = {
            'rating': 10,
            'review': 'VOLT SO FAST OUT OF RAMP ONE TAPPING THE GUY DEFAULT!',
        }

        self.url = reverse('edit_review', kwargs={'book_id': self.book.id})

    def test_edit_review_url(self):
        self.assertEqual(self.url, f'/library/books/{self.book.pk}/edit/')

    def test_post_edit_review_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.post(self.url, self.data, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200, fetch_redirect_response=True)
        self.assertTemplateUsed(response, 'login.html')

    def test_edit_review_redirects_when_different_user(self):
        self.client.login(username=self.another_user.username, password="Password123")
        self.assertTrue(self._is_logged_in())
        redirect_url = reverse('book_reviews', kwargs={'book_id': self.book.id})
        response = self.client.post(self.url, self.data, follow=True)
        messages_list = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200, fetch_redirect_response=True)
        self.assertTemplateUsed(response, 'book_reviews.html')

    '''Tests for user successfully editing the review and rating'''

    def test_successful_edit_rating_and_review_when_logged_in_as_user(self):
        self.client.login(username=self.user.username, password="Password123")
        self.assertTrue(self._is_logged_in())
        response = self.client.post(self.url, self.data, follow=True)
        self.book_review.refresh_from_db()
        messages_list = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.SUCCESS)
        redirect_url = reverse('book_reviews', kwargs={'book_id': self.book.id})
        self.assertTemplateUsed(response, 'book_reviews.html')
        self.assertEqual(self.book_review.user.id, self.user.id)
        self.assertEqual(self.book_review.rating, self.data['rating'])
        self.assertEqual(self.book_review.review, self.data['review'])
        self.assertRedirects(response, expected_url=redirect_url, status_code=302, target_status_code=200)

    def test_successful_edit_rating_when_logged_in_as_user(self):
        self.client.login(username=self.user.username, password="Password123")
        self.assertTrue(self._is_logged_in())
        self.data['review'] = 'Lorem Ipsum'
        response = self.client.post(self.url, self.data, follow=True)
        self.book_review.refresh_from_db()
        messages_list = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.SUCCESS)
        redirect_url = reverse('book_reviews', kwargs={'book_id': self.book.id})
        self.assertTemplateUsed(response, 'book_reviews.html')
        self.assertEqual(self.book_review.user.id, self.user.id)
        self.assertEqual(self.book_review.rating, self.data['rating'])
        self.assertEqual(self.book_review.review, self.data['review'])
        self.assertRedirects(response, expected_url=redirect_url, status_code=302, target_status_code=200)

    def test_successful_edit_review_when_logged_in_as_user(self):
        self.client.login(username=self.user.username, password="Password123")
        self.assertTrue(self._is_logged_in())
        self.data['rating'] = 1
        response = self.client.post(self.url, self.data, follow=True)
        self.book_review.refresh_from_db()
        messages_list = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.SUCCESS)
        redirect_url = reverse('book_reviews', kwargs={'book_id': self.book.id})
        self.assertTemplateUsed(response, 'book_reviews.html')
        self.assertEqual(self.book_review.user.id, self.user.id)
        self.assertEqual(self.book_review.rating, self.data['rating'])
        self.assertEqual(self.book_review.review, self.data['review'])
        self.assertRedirects(response, expected_url=redirect_url, status_code=302, target_status_code=200)

    '''Tests for user unsuccessfully editing the review and rating'''

    def test_unsuccessful_edit_review_when_logged_in_as_user(self):
        self.client.login(username=self.user.username, password="Password123")
        self.assertTrue(self._is_logged_in())
        self.data['rating'] = 'Hello'
        book_rating_before = self.book_review.rating
        book_review_before = self.book_review.review
        response = self.client.post(self.url, self.data, follow=True)
        self.book_review.refresh_from_db()
        self.assertTemplateUsed('edit_review.html')
        self.assertEqual(self.book_review.user.id, self.user.id)
        self.assertEqual(self.book_review.rating, book_rating_before)
        self.assertEqual(self.book_review.review, book_review_before)

    def test_no_review_to_edit(self):
        self.client.login(username=self.user.username, password="Password123")
        self.assertTrue(self._is_logged_in())
        self.url = reverse('edit_review', kwargs={'book_id': self.book.id})
        response = self.client.post(self.url, self.data, follow=True)
        redirect_url = reverse('book_reviews', kwargs={'book_id': self.book.id})
        messages_list = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200, fetch_redirect_response=True)
        self.assertTemplateUsed(response, 'book_reviews.html')

    def test_cannot_edit_other_users_rating_and_review(self):
        self.client.login(username=self.another_user.username, password="Password123")
        self.assertTrue(self._is_logged_in())
        book_rating_before = self.book_review.rating
        book_review_before = self.book_review.review
        response = self.client.post(self.url, self.data, follow=True)
        self.book_review.refresh_from_db()
        self.assertTemplateNotUsed('edit_review.html')
        messages_list = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertTrue(messages_list[0].level,messages.ERROR)
        self.assertEqual(str(messages_list[0]),"Book or review not found!")
        self.assertNotEqual(self.book_review.user.id, self.another_user.id)
        self.assertEqual(self.book_review.rating, book_rating_before)
        self.assertEqual(self.book_review.review, book_review_before)

    def test_cannot_edit_other_users_rating(self):
        self.client.login(username=self.another_user.username, password="Password123")
        self.assertTrue(self._is_logged_in())
        self.data['review'] = 'Lorem Ipsum'
        book_rating_before = self.book_review.rating
        book_review_before = self.book_review.review
        response = self.client.post(self.url, self.data, follow=True)
        self.book_review.refresh_from_db()
        self.assertTemplateNotUsed('edit_review.html')
        messages_list = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertTrue(messages_list[0].level,messages.ERROR)
        self.assertEqual(str(messages_list[0]),"Book or review not found!")
        self.assertNotEqual(self.book_review.user.id, self.another_user.id)
        self.assertEqual(self.book_review.rating, book_rating_before)
        self.assertEqual(self.book_review.review, book_review_before)

    def test_cannot_edit_other_users_review(self):
        self.client.login(username=self.another_user.username, password="Password123")
        self.assertTrue(self._is_logged_in())
        self.data['rating'] = 1
        book_rating_before = self.book_review.rating
        book_review_before = self.book_review.review
        response = self.client.post(self.url, self.data, follow=True)
        self.book_review.refresh_from_db()
        self.assertTemplateNotUsed('edit_review.html')
        messages_list = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertTrue(messages_list[0].level,messages.ERROR)
        self.assertEqual(str(messages_list[0]),"Book or review not found!")
        self.assertNotEqual(self.book_review.user.id, self.another_user.id)
        self.assertEqual(self.book_review.rating, book_rating_before)
        self.assertEqual(self.book_review.review, book_review_before)
