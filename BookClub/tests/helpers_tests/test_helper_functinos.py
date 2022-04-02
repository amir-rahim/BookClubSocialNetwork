"""Tests of the Helper funcitons in BookClub application."""
from django.test import TestCase, tag
from django.urls import reverse

from BookClub import helpers
from BookClub.models import User, Book, Club, ClubMembership, Forum, ForumPost, ForumComment, BookReview, BookReviewComment, Vote
from django.contrib.contenttypes.models import ContentType

from BookClub.tests.helpers import LogInTester

@tag('helpers')
class HelperFunctionsTestCase(TestCase, LogInTester):

    fixtures =[
        'BookClub/tests/fixtures/default_users.json',
        'BookClub/tests/fixtures/default_clubs.json',
        'BookClub/tests/fixtures/default_club_members.json',
        'BookClub/tests/fixtures/default_books.json',
        'BookClub/tests/fixtures/default_forum.json'
    ]

    def setUp(self):
        self.user2 = User.objects.get(pk=2)
        self.club2 = Club.objects.get(pk=2)

    def test_get_memberships_with_access_returns_empty_if_user_not_logged_in(self):
        home_url = reverse('home')
        response = self.client.get(home_url)
        self.assertEqual(self._is_logged_in(), False)
        memberships_with_access = helpers.get_memberships_with_access(response.wsgi_request.user)
        self.assertEqual(len(memberships_with_access), 0)

    def test_get_memberships_with_access(self):
        self.client.login(username=self.user2.username, password='Password123')
        home_url = reverse('home')
        response = self.client.get(home_url)
        self.assertEqual(self._is_logged_in(), True)
        memberships_with_access = helpers.get_memberships_with_access(response.wsgi_request.user)
        self.assertEqual(len(memberships_with_access), 2)

    def test_has_membership_with_access_for_unauthenticated_user(self):
        home_url = reverse('home')
        response = self.client.get(home_url)
        self.assertEqual(self._is_logged_in(), False)
        return_bool = helpers.has_membership_with_access(self.club2, response.wsgi_request.user)
        self.assertEqual(return_bool, False)

    def test_has_membership_with_access_for_authenticated_owner(self):
        self.client.login(username=self.user2.username, password='Password123')
        home_url = reverse('home')
        response = self.client.get(home_url)
        self.assertEqual(self._is_logged_in(), True)
        return_bool = helpers.has_membership_with_access(self.club2, response.wsgi_request.user)
        self.assertEqual(return_bool, True)

    def test_get_user_reputation(self):
        user = User.objects.get(pk=1)
        forum = Forum.objects.get(pk=1)
        book = Book.objects.get(pk=1)

        # make all ratable posts
        post = ForumPost.objects.create(forum=forum, title='My cool post', content='EVEN BETTER CONTENT', creator=user)
        comment = ForumComment.objects.create(post=post, content='great post!', creator=user)
        review = BookReview.objects.create(book=book, book_rating=5, title='It\'s ok', content='nothing incredible', creator=user)
        review_comment = BookReviewComment.objects.create(book_review=review, content='totally agree!', creator=user)

        post_vote = Vote.objects.create(
            creator=user,
            type=True,
            content_type=ContentType.objects.get_for_model(post.__class__),
            object_id=post.pk
        )
        post.add_vote(post_vote)

        comment_vote = Vote.objects.create(
            creator=user,
            type=False,
            content_type=ContentType.objects.get_for_model(comment.__class__),
            object_id=comment.pk
        )
        comment.add_vote(comment_vote)

        review_vote = Vote.objects.create(
            creator=user,
            type=True,
            content_type=ContentType.objects.get_for_model(review.__class__),
            object_id=review.pk
        )
        review.add_vote(review_vote)

        review_comment_vote = Vote.objects.create(
            creator=user,
            type=False,
            content_type=ContentType.objects.get_for_model(review_comment.__class__),
            object_id=review_comment.pk
        )
        review_comment.add_vote(review_comment_vote)

        return_rating = helpers.get_user_reputation(user)
        correct_rating = 0
        self.assertEqual(return_rating, correct_rating)
