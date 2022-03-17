from django.forms import ValidationError
from django.test import TestCase, tag
from django.contrib import messages
from django.contrib.messages import get_messages
from django.urls import reverse

from BookClub.models import BookReview, Book, BookReviewComment, User
from BookClub.tests.helpers import LogInTester

class CreateBookReviewCommentViewTestCase(TestCase,LogInTester):
    fixtures = [
        'BookClub/tests/fixtures/default_users.json',
        'BookClub/tests/fixtures/default_book_review_comments.json',
        'BookClub/tests/fixtures/default_book_reviews.json'
    ]
    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.another_user = User.objects.get(pk=6)
        self.book_review = BookReview.objects.get(pk=1)
        self.url = reverse('create_book_review_comment',kwargs={"book_review_id":self.book_review.id})
        self.data = {
            "content": "Comment on a Book Review."
        }



        
