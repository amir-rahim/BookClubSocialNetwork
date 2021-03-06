"""Unit testing of the Delete Review view"""
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase, tag
from django.urls import reverse

from BookClub.models import BookReview, User
from BookClub.tests.helpers import LogInTester, reverse_with_next


@tag('views', 'review', 'delete_book_review')
class DeleteBookReview(TestCase, LogInTester):
    """Tests for the Delete Review view"""
    fixtures = [
        "BookClub/tests/fixtures/default_users.json",
        "BookClub/tests/fixtures/default_clubs.json",
        "BookClub/tests/fixtures/default_books.json",
        "BookClub/tests/fixtures/default_book_reviews.json"]

    def setUp(self):
        self.bookreview = BookReview.objects.get(pk=1)
        self.review_author = self.bookreview.creator
        self.review_book = self.bookreview.book

        self.otherUser = User.objects.get(pk=6)

        self.url = reverse('delete_review', kwargs={'book_id': self.review_book.id})
        self.redirect_url = reverse('book_reviews', kwargs={'book_id': self.review_book.pk})

    def test_delete_book_review_url(self):
        self.assertEqual(self.url, f'/library/books/{self.bookreview.book.id}/delete/')

    def test_redirects_to_redirect_url(self):
        self.client.login(username=self.review_author.username, password="Password123")
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url)
        self.assertRedirects(response, self.redirect_url, status_code=302, target_status_code=200)

    """ Testing for unsuccessful deletes"""

    def test_delete_book_review_not_logged_in(self):
        """Test for a guest trying to delete a book review"""
        self.assertFalse(self._is_logged_in())
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.post(self.url)

        self.assertRedirects(response, redirect_url)
        self.client.post(self.url)

        bookreview_exists_before = BookReview.objects.filter(pk=self.bookreview.id).exists()
        self.assertTrue(bookreview_exists_before)
        bookreview_exists_after = BookReview.objects.filter(pk=self.bookreview.id).exists()
        self.assertTrue(bookreview_exists_after)
        self.assertEqual(bookreview_exists_before, bookreview_exists_after)

    def test_delete_book_review_other_logged_in(self):
        self.client.login(username=self.otherUser.username, password="Password123")
        self.assertTrue(self._is_logged_in())
        bookreview_exists_before = BookReview.objects.filter(pk=self.bookreview.id).exists()
        self.assertTrue(bookreview_exists_before)
        response = self.client.post(self.url)

        response_message = self.client.get(self.redirect_url)
        messages_list = list(response_message.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(str(messages_list[0]), 'You are not allowed to delete this review or Review doesn\'t exist')
        self.assertEqual(messages_list[0].level, messages.ERROR)

        bookreview_exists_after = BookReview.objects.filter(pk=self.bookreview.id).exists()
        self.assertEqual(bookreview_exists_before, bookreview_exists_after)

    def test_delete_invalid_book_review(self):
        self.client.login(username=self.otherUser.username, password="Password123")
        self.assertTrue(self._is_logged_in())
        invalid_url = reverse('delete_review', kwargs={"book_id": self.review_book.id})
        response = self.client.post(invalid_url)
        with self.assertRaises(ObjectDoesNotExist):
            BookReview.objects.get(id=self.bookreview.id + 999).exists()

        response_message = self.client.get(self.redirect_url)
        messages_list = list(response_message.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(str(messages_list[0]), 'You are not allowed to delete this review or Review doesn\'t exist')
        self.assertEqual(messages_list[0].level, messages.ERROR)

        self.assertRedirects(response, self.redirect_url, status_code=302, target_status_code=200)

    """Test for Successful delete"""

    def test_successful_delete(self):
        self.client.login(username=self.review_author.username, password="Password123")
        self.assertTrue(self._is_logged_in())
        bookreview_exists_before = BookReview.objects.filter(pk=self.bookreview.id).exists()
        self.assertTrue(bookreview_exists_before)
        response = self.client.post(self.url)

        response_message = self.client.get(self.redirect_url)
        messages_list = list(response_message.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(str(messages_list[0]), 'You have deleted the review')
        self.assertEqual(messages_list[0].level, messages.SUCCESS)

        bookreview_exists_after = BookReview.objects.filter(pk=self.bookreview.id).exists()
        self.assertNotEqual(bookreview_exists_before, bookreview_exists_after)
        self.assertRedirects(response, self.redirect_url, status_code=302, target_status_code=200)
