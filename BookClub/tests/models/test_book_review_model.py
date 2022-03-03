import datetime
from django.forms import ValidationError
from BookClub.models import Book, User, BookReview
from django.db import IntegrityError, models
from django.test import TestCase, tag

from BookClub.models.user import User


@tag('review', 'book', 'models')
class BookReviewModelTestCase(TestCase):
    
    fixtures=[
        'BookClub/tests/fixtures/default_books.json',
        'BookClub/tests/fixtures/default_users.json',
        'BookClub/tests/fixtures/default_book_reviews.json',
    ]
    
    def setUp(self):
        self.book1 = Book.objects.get(pk=1)
        self.book2 = Book.objects.get(pk=2)
        self.book3 = Book.objects.get(pk=3)
        self.user1 = User.objects.get(pk=1)
        self.user2 = User.objects.get(pk=2)
        self.review1 = BookReview.objects.get(pk=1)
        
    def assertValid(self):
        try:
            self.review1.full_clean()
        except(ValidationError):
            self.fail('Review should be valid')
            
    def assertInvalid(self):
        with self.assertRaises(Exception):
            self.review1.full_clean()
            
    def test_review1_is_valid(self):
        self.assertValid()
            
    def test_book_cannot_be_null(self):
        self.review1.book = None
        self.assertInvalid()
        
    def test_rating_cannot_blank(self):
        self.review1.rating = None
        self.assertInvalid()
        
    def test_rating_valid_choices(self):
        for i in range(0,10):
            self.review1.rating = i
            self.assertValid()
        
    def test_rating_cannot_greater_than_10(self):
        self.review1.rating = 11
        self.assertInvalid()
        
    def test_rating_cannot_less_than_0(self):
        self.review1.rating =ValidationError
        
    def test_review_can_be_1to1024char(self):
        self.review1.review = "1"
        self.assertValid()
        self.review1.review = "1" * 1024
        self.assertValid()
        
    def test_review_cannot_be_1025_chars(self):
        self.review1.review = "1" * 1025
        self.assertInvalid()
        
    def test_user_cannot_be_blank(self):
        self.review1.user = None
        self.assertInvalid()
        
    def test_user_book_combo_must_be_unique(self):
        reviewCopy = BookReview.objects.get(pk=1)
        reviewCopy.pk = None
        with self.assertRaises(Exception):
            reviewCopy.save()
            
    def test_user_can_have_multiple_reviews_different_books(self):
        review2 = BookReview.objects.create(
            book = self.book3, 
            rating = 1,
            review = "",
            user = self.user1,            
        )
        try:
            review2.full_clean()
        except ValidationError:
            self.fail('Review2 should be valid')
            
    def test_book_can_have_multiple_reviews_by_different_users(self):
        review2 = BookReview.objects.create(
            book = self.book1, 
            rating = 1,
            review = "",
            user = self.user2,            
        )
        try:
            review2.full_clean()
        except ValidationError:
            self.fail('Review2 should be valid')