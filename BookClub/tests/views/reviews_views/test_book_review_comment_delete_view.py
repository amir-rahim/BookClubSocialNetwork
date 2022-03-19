from django.forms import ValidationError
from django.shortcuts import redirect
from django.test import TestCase, tag
from django.contrib import messages
from django.contrib.messages import get_messages
from django.urls import reverse

from BookClub.models import BookReview, Book, BookReviewComment, User
from BookClub.tests.helpers import LogInTester, reverse_with_next

@tag('delete','review','reviews','delete_book_review_comment','delete_comment')
class DeleteBookReviewCommentTestCase(TestCase,LogInTester):
    """Tests for Delete Book Review Comment"""
    fixtures = [
        'BookClub/tests/fixtures/default_users.json',
        'BookClub/tests/fixtures/default_book_review_comments.json',
        'BookClub/tests/fixtures/default_books.json',
        'BookClub/tests/fixtures/default_book_reviews.json'
    ]

    def setUp(self):
        self.creator = User.objects.get(pk=1)
        self.another_user = User.objects.get(pk=6)

        self.book_review_comment = BookReviewComment.objects.get(pk=1)
        self.book_review = self.book_review_comment.book_review
        self.book = self.book_review.book

        self.url = reverse("delete_review_comment",kwargs = {
            "book_id": self.book.id,
            "review_id": self.book_review.id,
            "comment_id": self.book_review_comment.id
        })

    def test_delete_book_review_comment_url(self):
        self.assertEqual(self.url,f"/library/books/{self.book.id}/review/{self.book_review.id}/comment/{self.book_review_comment.id}/delete/")

    """Testing unsucessful deletes"""
    def test_redirect_when_not_logged_in(self):
        self.assertFalse(self._is_logged_in())
        redirect_url = reverse_with_next('login',self.url)
        response = self.client.post(self.url,follow=True)
        self.assertRedirects(response,redirect_url,status_code=302,target_status_code=200,fetch_redirect_response=True)
        self.assertTemplateUsed("login.html")

    def test_delete_book_review_comment_when_not_logged_in(self):
        book_review_comment_count_before = BookReviewComment.objects.count()
        response = self.client.post(self.url,follow=True)
        book_review_comment_count_after = BookReviewComment.objects.count()
        self.assertEqual(book_review_comment_count_before,book_review_comment_count_after)

    """Testing when not the creator"""
    def test_redirect_when_not_creator(self):
        self.client.login(username=self.another_user.username, password="Password123")
        self.assertTrue(self._is_logged_in())
        redirect_url = reverse('book_review', kwargs={"book_id": self.book.id,"review_id": self.book_review.id})
        response = self.client.post(self.url, follow=True)
        self.assertRedirects(response, redirect_url,status_code=302, target_status_code=200, fetch_redirect_response=True)

    def test_delete_book_review_comment_when_not_creator(self):
        self.client.login(username = self.another_user.username,password = "Password123")
        self.assertTrue(self._is_logged_in())
        book_review_comment_count_before = BookReviewComment.objects.count()
        response = self.client.post(self.url,follow=True)
        book_review_comment_count_after = BookReviewComment.objects.count()
        self.assertEqual(book_review_comment_count_before,book_review_comment_count_after)
        messages_list = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        self.assertEqual(str(messages_list[0]),"Access denied!")

    """Testing with an invalid comment id"""
    def test_redirect_with_invalid_comment_id(self):
        self.client.login(username=self.creator.username,password="Password123")
        self.assertTrue(self._is_logged_in())
        url = reverse("delete_review_comment",kwargs = {
            "book_id": self.book.id,
            "review_id": self.book_review.id,
            "comment_id": 9999
        })
        redirect_url = reverse("book_review",kwargs={"book_id":self.book.id,"review_id": self.book_review.id})
        response = self.client.post(url,follow=True)
        self.assertRedirects(response, redirect_url,status_code=302, target_status_code=200, fetch_redirect_response=True)

    def test_delete_book_review_comment_with_invalid_comment_id(self):
        self.client.login(username = self.creator.username,password = "Password123")
        self.assertTrue(self._is_logged_in())
        book_review_comment_count_before = BookReviewComment.objects.count()
        url = reverse("delete_review_comment",kwargs = {
            "book_id": self.book.id,
            "review_id": self.book_review.id,
            "comment_id": 9999
        })
        response = self.client.post(url,follow=True)
        book_review_comment_count_after = BookReviewComment.objects.count()
        self.assertEqual(book_review_comment_count_before,book_review_comment_count_after)
        messages_list = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        self.assertEqual(str(messages_list[0]),"The comment you tried to delete was not found!")

    
    """Testing the only valid delete"""
    
    def test_delete_book_review_comment_when_creator(self):
        self.client.login(username = self.creator.username,password = "Password123")
        self.assertTrue(self._is_logged_in())
        book_review_comment_count_before = BookReviewComment.objects.count()
        response = self.client.post(self.url,follow=True)
        book_review_comment_count_after = BookReviewComment.objects.count()
        redirect_url = reverse('book_review', kwargs={"book_id": self.book.id,"review_id": self.book_review.id})
        response = self.client.post(self.url, follow=True)
        self.assertRedirects(response, redirect_url,status_code=302, target_status_code=200, fetch_redirect_response=True)
        self.assertNotEqual(book_review_comment_count_before,book_review_comment_count_after)
        self.assertEqual(book_review_comment_count_before-1,book_review_comment_count_after)
    
    