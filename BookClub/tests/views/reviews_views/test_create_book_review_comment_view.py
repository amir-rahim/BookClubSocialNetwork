from django.forms import ValidationError
from django.shortcuts import redirect
from django.test import TestCase, tag
from django.contrib import messages
from django.contrib.messages import get_messages
from django.urls import reverse

from BookClub.models import BookReview, Book, BookReviewComment, User
from BookClub.tests.helpers import LogInTester, reverse_with_next

@tag('book_review','book_review_comment','create_book_review_comment','review')
class CreateCommentForReviewTestCase(TestCase,LogInTester):
    """Tests for Creating Book Review Comment View"""
    fixtures = [
        'BookClub/tests/fixtures/default_users.json',
        'BookClub/tests/fixtures/default_book_review_comments.json',
        'BookClub/tests/fixtures/default_books.json',
        'BookClub/tests/fixtures/default_book_reviews.json'
    ]
    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.another_user = User.objects.get(pk=6)
        self.book_review = BookReview.objects.get(pk=1)
        self.book = self.book_review.book
        self.url = reverse('comment_review',kwargs={
            "book_id": self.book.id,
            "review_id": self.book_review.id
            })
        self.data = {
            "content": "New Comment on a book review"
        }


    def test_create_book_review_comment_url(self):
        self.client.login(username = self.another_user,password="Password123")
        self.assertTrue(self._is_logged_in())
        self.assertEqual(self.url, f'/library/books/{self.book.id}/review/{self.book_review.id}/comment/')
        
    def test_redirect_when_not_logged_in(self):
        self.assertFalse(self._is_logged_in())
        redirect_url = reverse_with_next('login',self.url)
        response = self.client.post(self.url, self.data, follow=True)
        self.assertRedirects(
            response,
            redirect_url,
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True
            )

    def test_create_book_review_comment_when_not_logged_in(self):
        self.assertFalse(self._is_logged_in())
        book_review_count_before = BookReviewComment.objects.count()
        redirect_url = reverse_with_next('login',self.url)
        response = self.client.post(self.url,self.data,follow=True)
        self.assertRedirects(
            response,
            redirect_url,
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True
            )
        self.assertTemplateUsed(response,"login.html")
        book_review_count_after = BookReviewComment.objects.count()
        self.assertEqual(book_review_count_before,book_review_count_after)

    def test_create_book_review_comment_when_logged_in(self):
        self.client.login(username=self.another_user.username, password="Password123")
        redirect_url = reverse('book_review', kwargs={"book_id": self.book.id,"review_id": self.book_review.id})
        book_review_count_before = BookReviewComment.objects.count()
        response = self.client.post(self.url, self.data, follow=True)
        self.assertRedirects(
            response,
            redirect_url,
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True
            )
        book_review_count_after = BookReviewComment.objects.count()
        self.assertEqual(book_review_count_after, book_review_count_before+1)

    def test_user_can_create_multiple_comments_on_same_review(self):
        self.client.login(username=self.user.username, password="Password123")
        redirect_url = reverse('book_review', kwargs={"book_id": self.book.id,"review_id": self.book_review.id})
        book_review_count_before = BookReviewComment.objects.count()
        response = self.client.post(self.url, self.data, follow=True)
        self.data['content'] = "Not too shabby"
        self.assertContains(response,"Not too shabby")
        self.assertRedirects(
            response,
            redirect_url,
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True
            )
        
        self.data['content'] = "Totally new comment"
        response2 = self.client.post(self.url, self.data, follow=True)
        self.assertContains(response2,"Totally new comment")
        book_review_count_after = BookReviewComment.objects.count()
        self.assertEqual(book_review_count_after, book_review_count_before+2)

    def test_create_invalid_book_review_comment(self):
        self.client.login(username=self.user.username, password="Password123")
        redirect_url = reverse('book_review', kwargs={"book_id": self.book.id,"review_id": self.book_review.id})
        book_review_count_before = BookReviewComment.objects.count()
        self.data['content'] = "a"*1025
        response = self.client.post(self.url,self.data,follow=True)
        self.assertRedirects(
            response,
            redirect_url,
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True)
        messages_list = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        self.assertEqual(str(messages_list[0]),"There was an error making that comment, try again!")
        book_review_count_after = BookReviewComment.objects.count()
        self.assertEqual(book_review_count_after, book_review_count_before)

    def test_create_comment_on_invalid_book_review(self):
        self.client.login(username=self.user.username, password="Password123")
        redirect_url = reverse('book_review', kwargs={"book_id": self.book.id,"review_id": 999})
        book_review_count_before = BookReviewComment.objects.count()
        self.url = reverse("comment_review",kwargs={"book_id": self.book.id,"review_id": 999})
        response = self.client.post(self.url,self.data,follow=True)
        self.assertRedirects(
            response,
            redirect_url,
            status_code=302,
            target_status_code=404,
            fetch_redirect_response=True)
        messages_list = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        self.assertEqual(str(messages_list[0]),"There was an error making that comment, try again!")
        book_review_count_after = BookReviewComment.objects.count()
        self.assertEqual(book_review_count_after, book_review_count_before)