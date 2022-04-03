"""Unit testing of the Remove Featured Book view."""
from django.contrib.messages import get_messages
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase, tag
from django.urls import reverse

from BookClub.models import User, Club, ClubMembership, Book, FeaturedBooks
from BookClub.tests.helpers import reverse_with_next


@tag('views', 'club', 'feature_book')
class RemoveFeaturedBookViewTestCase(TestCase):
    """Test the Remove Featured Book view."""

    fixtures = [
        "BookClub/tests/fixtures/default_users.json",
        "BookClub/tests/fixtures/default_clubs.json",
        "BookClub/tests/fixtures/default_books.json",
    ]

    def setUp(self):
        self.owner = User.objects.get(pk=1)
        self.moderator = User.objects.get(pk=2)
        self.member = User.objects.get(pk=3)
        self.applicant = User.objects.get(pk=4)

        self.book = Book.objects.get(pk=1)
        self.club = Club.objects.get(pk=2)
        self.private_club = Club.objects.get(pk=3)
        self.url = reverse('remove_featured_book', kwargs={'club_url_name': self.club.club_url_name, 'book_id': self.book.id})
        self.url_private_club = reverse('remove_featured_book', kwargs={'club_url_name': self.private_club.club_url_name, 'book_id': self.book.id})
        
        ClubMembership.objects.create(user=self.owner, club=self.club, membership=ClubMembership.UserRoles.OWNER)
        ClubMembership.objects.create(user=self.moderator, club=self.club, membership=ClubMembership.UserRoles.MODERATOR)
        ClubMembership.objects.create(user=self.member, club=self.club, membership=ClubMembership.UserRoles.MEMBER)
        ClubMembership.objects.create(user=self.applicant, club=self.private_club, membership=ClubMembership.UserRoles.APPLICANT)
        ClubMembership.objects.create(user=self.owner, club=self.private_club, membership=ClubMembership.UserRoles.OWNER)

        FeaturedBooks.objects.create(club=self.club, book=self.book)
        FeaturedBooks.objects.create(club=self.private_club, book=self.book)

    def test_remove_featured_book_url(self):
        self.assertEqual(self.url, f'/club/{self.club.club_url_name}/featured/{self.book.id}/remove')

    def test_post_remove_featured_book_redirects_when_not_logged_in(self):
        featured_book_count_before = FeaturedBooks.get_books(self.club).count()
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.post(self.url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200, fetch_redirect_response=True)
        self.assertTemplateUsed(response, 'authentication/login.html')
        featured_book_count_after = FeaturedBooks.get_books(self.club).count()
        self.assertEqual(featured_book_count_before, featured_book_count_after)

    def test_get_remove_featured_book_redirects_when_not_logged_in(self):
        featured_book_count_before = FeaturedBooks.get_books(self.club).count()
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200, fetch_redirect_response=True)
        self.assertTemplateUsed(response, 'authentication/login.html')
        featured_book_count_after = FeaturedBooks.get_books(self.club).count()
        self.assertEqual(featured_book_count_before, featured_book_count_after)

    def test_get_remove_featured_book_redirects_to_club_dashboard(self):
        """Test for redirecting user to club dashboard when used get method."""

        self.client.login(username=self.owner.username, password='Password123')

        response = self.client.get(self.url)
        redirect_url = reverse('club_dashboard', kwargs={'club_url_name': self.club.club_url_name})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    '''Tests for users successfully removing featured book'''

    def test_owner_can_remove_featured_book(self):
        self.client.login(username=self.owner.username, password='Password123')
        before_count = FeaturedBooks.get_books(self.club).count()
        response = self.client.post(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        after_count = FeaturedBooks.get_books(self.club).count()
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'You have removed the book from featured.')
        self.assertEqual(after_count, before_count - 1)
        self.assertTemplateUsed(response, 'clubs/club_dashboard.html')
        self.assertFalse(FeaturedBooks.objects.filter(club=self.club, book=self.book).exists())

    def test_moderator_can_remove_featured_book(self):
        self.client.login(username=self.moderator.username, password='Password123')
        before_count = FeaturedBooks.get_books(self.club).count()
        response = self.client.post(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'You have removed the book from featured.')
        after_count = FeaturedBooks.get_books(self.club).count()
        self.assertEqual(after_count, before_count - 1)
        self.assertTemplateUsed(response, 'clubs/club_dashboard.html')
        self.assertFalse(FeaturedBooks.objects.filter(club=self.club, book=self.book).exists())

    def test_member_cannot_remove_featured_book(self):
        self.client.login(username=self.member.username, password='Password123')
        before_count = FeaturedBooks.get_books(self.club).count()
        response = self.client.post(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'You are not allowed to edit this!')
        after_count = FeaturedBooks.get_books(self.club).count()
        self.assertEqual(after_count, before_count)
        self.assertTemplateUsed(response, 'clubs/club_dashboard.html')
        self.assertTrue(FeaturedBooks.objects.filter(club=self.club, book=self.book).exists())

    def test_applicant_cannot_remove_featured_book(self):
        self.client.login(username=self.applicant.username, password='Password123')
        before_count = FeaturedBooks.get_books(self.private_club).count()
        response = self.client.post(self.url_private_club, follow=True)
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 2)
        self.assertEqual(str(messages[1]), 'This club is private')
        self.assertEqual(str(messages[0]), 'You are not allowed to edit this!')
        after_count = FeaturedBooks.get_books(self.private_club).count()
        self.assertEqual(after_count, before_count)
        self.assertTemplateUsed(response, 'clubs/available_clubs.html')
        self.assertTrue(FeaturedBooks.objects.filter(club=self.private_club, book=self.book).exists())

    def test_cannot_remove_not_featured_book(self):
        book = Book.objects.get(pk=2)
        self.client.login(username=self.owner.username, password='Password123')
        url = reverse('remove_featured_book', kwargs={'club_url_name': self.club.club_url_name, 'book_id': book.id})
        before_count = FeaturedBooks.get_books(self.club).count()
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Error, invalid data.")
        after_count = FeaturedBooks.get_books(self.club).count()
        self.assertEqual(after_count, before_count)
        self.assertTemplateUsed(response, 'clubs/club_dashboard.html')

    def test_cannot_remove_featured_invalid_book(self):
        self.client.login(username=self.owner.username, password='Password123')
        before_count = FeaturedBooks.get_books(self.club).count()
        url = reverse('remove_featured_book', kwargs={'club_url_name': self.club.club_url_name, 'book_id': 123456})
        response = self.client.post(url, follow=True)
        with self.assertRaises(ObjectDoesNotExist):
            Book.objects.get(pk=123456).exists()
        self.assertEqual(response.status_code, 200)
        after_count = FeaturedBooks.get_books(self.club).count()
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Error, invalid data.')
        self.assertEqual(after_count, before_count)
        self.assertTemplateUsed(response, 'clubs/club_dashboard.html')

    def test_cannot_remove_featured_book_from_invalid_club(self):
        self.client.login(username=self.owner.username, password='Password123')
        before_count = FeaturedBooks.get_books(self.club).count()
        response = self.client.post(reverse('remove_featured_book', kwargs={'club_url_name': 'some_random_name', 'book_id': self.book.id}), follow=True)
        with self.assertRaises(ObjectDoesNotExist):
            Club.objects.get(club_url_name="some_random_name").exists()
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Error, invalid data.')
        after_count = FeaturedBooks.get_books(self.club).count()
        self.assertEqual(after_count, before_count)
    
