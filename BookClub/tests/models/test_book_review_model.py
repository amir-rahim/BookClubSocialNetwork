import datetime
from django.forms import ValidationError
from BookClub.models import Book, User, BookReview, BookReviewComment, UserRecommendations
from django.db import IntegrityError, models
from django.urls import reverse
from django.test import TestCase, tag
from BookClub.models.club import Club
from BookClub.models.recommendations import ClubRecommendations

from BookClub.models.user import User


@tag('models', 'review')
class BookReviewModelTestCase(TestCase):

    fixtures=[
        'BookClub/tests/fixtures/default_books.json',
        'BookClub/tests/fixtures/default_users.json',
        'BookClub/tests/fixtures/default_book_reviews.json',
        'BookClub/tests/fixtures/default_book_review_comments.json',
        'BookClub/tests/fixtures/default_clubs.json',
        'BookClub/tests/fixtures/default_club_members.json'
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
        self.review1.book_rating = None
        self.assertInvalid()

    def test_rating_valid_choices(self):
        for i in range(0,10):
            self.review1.book_rating = i
            self.assertValid()

    def test_rating_cannot_greater_than_10(self):
        self.review1.book_rating = 11
        self.assertInvalid()

    def test_rating_cannot_less_than_0(self):
        self.review1.book_rating = -1
        self.assertInvalid()

    def test_review_cannot_be_blank(self):
        self.review1.content = ""
        self.assertInvalid()

    def test_review_can_be_1to1024char(self):
        self.review1.content = "1"
        self.assertValid()
        self.review1.content = "1" * 1024
        self.assertValid()

    def test_review_cannot_be_1025_chars(self):
        self.review1.content = "1" * 1025
        self.assertInvalid()

    def test_title_can_be_1to30char(self):
        self.review1.title = "1"
        self.assertValid()
        self.review1.title = "1"*30
        self.assertValid()

    def test_user_cannot_be_blank(self):
        self.review1.creator = None
        self.assertInvalid()

    def test_user_book_combo_must_be_unique(self):
        reviewCopy = BookReview.objects.get(pk=1)
        reviewCopy.pk = None
        with self.assertRaises(Exception):
            reviewCopy.save()

    def test_user_can_have_multiple_reviews_different_books(self):
        review2 = BookReview.objects.create(
            book=self.book3,
            book_rating=1,
            title="Not good",
            content="read title",
            creator=self.user1,
        )
        try:
            review2.full_clean()
        except ValidationError:
            self.fail('Review2 should be valid')

    def test_book_can_have_multiple_reviews_by_different_users(self):
        review2 = BookReview.objects.create(
            book=self.book1,
            book_rating=1,
            title="Bad",
            content="read title",
            creator=self.user2,
        )
        try:
            review2.full_clean()
        except ValidationError:
            self.fail('Review2 should be valid')

    def test_get_comments(self):
        self.assertTrue(self.review1.get_comments()!=None)

    def test_get_absolute_url(self):
        return_url = self.review1.get_absolute_url()
        correct_url = '/library/books/1/review/1/'
        self.assertEqual(return_url, correct_url)

    def test_get_delete_url(self):
        delete_url = reverse('delete_review',kwargs={'book_id': self.review1.book.pk})
        self.assertEqual(self.review1.get_delete_url(),delete_url)

    def test_str(self):
        self.assertEqual(self.review1.str(),"1/10 rating & review by johndoe on \"Classical Mythology\"")
        self.assertEqual(str(self.review1),"1/10 rating & review by johndoe on \"Classical Mythology\"")
        self.assertEqual(self.review1.get_delete_str(),"1/10 rating & review by johndoe on \"Classical Mythology\"")

    def test_save_executes_safely_when_user_has_no_modifications(self):
        recommendation_exists = UserRecommendations.objects.filter(user=self.user1).exists()
        self.assertFalse(recommendation_exists)
        self.review1.book_rating = 5
        self.review1.save()
        recommendation_exists = UserRecommendations.objects.filter(user=self.user1).exists()
        self.assertFalse(recommendation_exists)

    def test_save_changes_user_modified(self):
        rec = UserRecommendations.objects.create(user=self.user1)
        rec.modified = False
        rec.save()
        recommendation_exists = UserRecommendations.objects.filter(
            user=self.user1).exists()
        self.review1.book_rating = 5
        self.review1.save()
        recommendation_exists = UserRecommendations.objects.filter(
            user=self.user1)
        self.assertTrue(recommendation_exists)
        rec.refresh_from_db()
        self.assertTrue(rec.modified)

    def test_save_changes_club_modified(self):
        club = Club.objects.get(pk=1)
        rec = ClubRecommendations.objects.create(club=club)
        rec.modified = False
        rec.save()
        recommendation_exists = ClubRecommendations.objects.filter(
            club=club).exists()
        self.review1.book_rating = 5
        self.review1.save()
        recommendation_exists = ClubRecommendations.objects.filter(
            club=club)
        self.assertTrue(recommendation_exists)
        rec.refresh_from_db()
        self.assertTrue(rec.modified)

@tag('models', 'reviewcomment')
class BookReviewCommentTestCase(TestCase):
    fixtures = [
        'BookClub/tests/fixtures/default_users.json',
        'BookClub/tests/fixtures/default_books.json',
        'BookClub/tests/fixtures/default_book_reviews.json',
        'BookClub/tests/fixtures/default_book_review_comments.json',
    ]

    def setUp(self):
        self.bookReviewComment = BookReviewComment.objects.get(pk=1)
        self.bookReview = self.bookReviewComment.book_review
        self.originalPoster = self.bookReview.creator

    def assertValid(self):
        try:
            self.bookReviewComment.full_clean()
        except(ValidationError):
            self.fail('Test user created object should be valid')

    def assertInvalid(self):
        with self.assertRaises(ValidationError):
            self.bookReviewComment.full_clean()

    def test_valid(self):
        self.assertValid()

    def test_book_review_comment_can_be_up_to_240_chars(self):
        self.bookReviewComment.content = "x"
        self.assertValid()
        self.bookReviewComment.content = "x"*240
        self.assertValid()

    def test_book_review_comment_cant_be_more_than_240(self):
        self.bookReviewComment.content = "x"*9999
        self.assertInvalid()

    def test_votes_can_be_empty(self):
        self.bookReviewComment.votes.clear()
        self.assertValid()

    def test_rating_can_not_be_blank_or_null(self):
        self.bookReviewComment.rating = None
        self.assertInvalid()
        self.bookReviewComment.rating = ""
        self.assertInvalid()

    def test_str(self):
        self.assertEqual(self.bookReviewComment.str(),"Comment by johndoe on 1/10 rating & review by johndoe on \"Classical Mythology\"")
        self.assertEqual(str(self.bookReviewComment),"Comment by johndoe on 1/10 rating & review by johndoe on \"Classical Mythology\"")
        self.assertEqual(self.bookReviewComment.get_delete_str(),"Comment by johndoe on 1/10 rating & review by johndoe on \"Classical Mythology\"")

    def test_get_delete_url(self):
        delete_url = reverse('delete_review_comment',kwargs={
            'book_id': self.bookReview.book.id,
            'review_id': self.bookReview.id,
            'comment_id': self.bookReviewComment.id
            })
        self.assertEqual(self.bookReviewComment.get_delete_url(),delete_url)
