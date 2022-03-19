from urllib import response
from django.forms import ValidationError
from django.shortcuts import redirect
from django.test import TestCase, tag
from django.contrib import messages
from django.contrib.messages import get_messages
from django.urls import reverse

from BookClub.models import BookReview, User
from BookClub.tests.helpers import LogInTester, reverse_with_next

@tag("review","book_review_view","book_review")
class BookReviewViewTestCase(TestCase,LogInTester):

    fixtures = [
        'BookClub/tests/fixtures/default_users.json',
        'BookClub/tests/fixtures/default_book_review_comments.json',
        'BookClub/tests/fixtures/default_books.json',
        'BookClub/tests/fixtures/default_book_reviews.json',
        'BookClub/tests/fixtures/more_book_review_comments.json',
        'BookClub/tests/fixtures/more_book_reviews.json'
    ]

    def setUp(self):
        self.book_review = BookReview.objects.get(pk=1)
        self.another_book_review = BookReview.objects.get(pk=3)
        self.no_comment_book_review = BookReview.objects.get(pk=4)

        self.creator_of_main_review = User.objects.get(pk=1)
        self.creator_of_other_review = User.objects.get(pk=3)
        self.other_user = User.objects.get(pk=6)
        self.creator_of_commentless_review = self.other_user

        self.main_review_url = reverse("book_review",kwargs = {"book_id": self.book_review.book_id,"review_id": self.book_review.id})
        self.other_review_url = reverse("book_review",kwargs = {"book_id": self.another_book_review.book_id,"review_id": self.another_book_review.id})
        self.no_comment_review_url = reverse("book_review",kwargs = {"book_id": self.no_comment_book_review.book_id,"review_id": self.no_comment_book_review.id})

    def test_book_review_detail_view_url(self):
        self.assertEqual(self.main_review_url,f'/library/books/{self.book_review.book.id}/review/{self.book_review.id}/')
        self.assertEqual(self.other_review_url,f'/library/books/{self.another_book_review.book.id}/review/{self.another_book_review.id}/')

    def test_can_view_forum_when_not_logged_in(self):
        self.assertFalse(self._is_logged_in())
        response = self.client.get(self.main_review_url)
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,"review_details.html")

    def test_can_view_forum_when_logged_in(self):
        self.client.login(username=self.creator_of_main_review.username,password="Password123")
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.main_review_url)
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,"review_details.html")
    
    def test_guest_can_see_review_content(self):
        response = self.client.get(self.main_review_url)
        self.assertContains(response,f'Review by {self.book_review.creator}')
        self.assertContains(response,f'Posted by: {self.book_review.creator}')
        self.assertContains(response,self.book_review.title)
        self.assertContains(response,self.book_review.content)
        self.assertContains(response,f'{self.book_review.book_rating}/10')
        review_comments = list(response.context['comments'])
        self.assertEqual(len(review_comments), 1)
    
    def test_other_user_can_see_review_content(self):
        self.client.login(username=self.other_user.username,password="Password123")
        response = self.client.get(self.main_review_url)
        self.assertContains(response,f'Review by {self.book_review.creator}')
        self.assertContains(response,f'Posted by: {self.book_review.creator}')
        self.assertContains(response,self.book_review.title)
        self.assertContains(response,self.book_review.content)
        self.assertContains(response,f'{self.book_review.book_rating}/10')

    def test_creator_can_see_review_content(self):
        self.client.login(username=self.creator_of_main_review.username,password="Password123")
        response = self.client.get(self.main_review_url)
        self.assertContains(response,f'Review by {self.book_review.creator}')
        self.assertContains(response,f'Posted by: {self.book_review.creator}')
        self.assertContains(response,self.book_review.title)
        self.assertContains(response,self.book_review.content)
        self.assertContains(response,f'{self.book_review.book_rating}/10')

    def test_guest_can_see_comments(self):
        response = self.client.get(self.other_review_url)
        review_comments = list(response.context['comments'])
        self.assertContains(response,f"by {self.another_book_review.creator}" )
        self.assertEqual(len(review_comments), 2)

    def test_other_user_can_see_comments(self):
        self.client.login(username=self.other_user.username,password="Password123")
        response = self.client.get(self.other_review_url)
        review_comments = list(response.context['comments'])
        self.assertContains(response,f"by {self.another_book_review.creator}" )
        self.assertEqual(len(review_comments), 2)

    def test_creator_can_see_comments(self):
        self.client.login(username=self.creator_of_other_review.username,password="Password123")
        response = self.client.get(self.other_review_url)
        review_comments = list(response.context['comments'])
        self.assertContains(response,f"by {self.another_book_review.creator}" )
        self.assertEqual(len(review_comments), 2)

    def guest_see_no_comments_on_commentless_review(self):
        response = self.client.get(self.no_comment_review_url)
        review_comments = list(response.context['comments'])
        self.assertEqual(len(review_comments), 0)
        self.assertContains(response,"There are no comments for this review. Comment using the reply button on the review.")

    def test_other_user_see_no_comments_on_commentless_review(self):
        self.client.login(username=self.other_user.username,password="Password123")
        response = self.client.get(self.no_comment_review_url)
        review_comments = list(response.context['comments'])
        self.assertEqual(len(review_comments), 0)
        self.assertContains(response,"There are no comments for this review. Comment using the reply button on the review.")

    def test_creator_can_see_no_comments_on_commentless_review(self):
        self.client.login(username=self.creator_of_commentless_review.username,password="Password123")
        response = self.client.get(self.no_comment_review_url)
        review_comments = list(response.context['comments'])
        self.assertEqual(len(review_comments), 0)
        self.assertContains(response,"There are no comments for this review. Comment using the reply button on the review.")

    def test_creator_can_see_book_review_buttons(self):
        self.client.login(username = self.creator_of_main_review.username,password = "Password123")
        response = self.client.get(self.main_review_url)
        self.assertContains(response,f"<button class=\"button is-danger\">Delete</button>")
        self.assertContains(response,"""<button class="button is-success is-rounded" aria-label="Edit Review">
                                    <span class="icon">
                                        <i class="fa-solid fa-wand-magic-sparkles"></i>
                                    </span>
                                    <span>Edit</span>
                                </button>""")

    def test_not_creator_cannot_see_book_review_buttons(self):
        response = self.client.get(self.main_review_url)
        self.assertNotContains(response,"""<button class="button is-success is-rounded" aria-label="Edit Review">
                                    <span class="icon">
                                        <i class="fa-solid fa-wand-magic-sparkles"></i>
                                    </span>
                                    <span>Edit</span>
                                </button>""")

        self.assertNotContains(response,f"<button class=\"button is-danger\">Delete</button>")
        self.client.login(username = self.other_user.username,password = "Password123")

        response2 = self.client.get(self.main_review_url)
        self.assertNotContains(response2,"""<button class="button is-success is-rounded" aria-label="Edit Review">
                                    <span class="icon">
                                        <i class="fa-solid fa-wand-magic-sparkles"></i>
                                    </span>
                                    <span>Edit</span>
                                </button>""")
        self.assertNotContains(response2,f"<button class=\"button is-danger\">Delete</button>")

    def test_not_creator_cannot_see_book_review_comment_buttons(self):
        self.client.login(username = self.other_user.username , password = "Password123")
        response = self.client.get(self.main_review_url)
        self.assertNotContains(response,f"<button class=\"button is-danger\">Delete</button>")

    def test_creator_can_see_book_review_comment_buttons(self):
        self.client.login(username = self.creator_of_main_review,password = "Password123")
        response = self.client.get(self.main_review_url)
        self.assertContains(response,f"<button class=\"button is-danger\">Delete</button>")
        
        

