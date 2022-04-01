"""Test the Create Featured Book view."""
from django.contrib import messages
from django.contrib.messages import get_messages
from django.test import TestCase, tag
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist

from BookClub.forms import FeatureBookForm
from BookClub.models import User, Club, ClubMembership, Book, FeaturedBooks
from BookClub.tests.helpers import reverse_with_next



@tag('club', 'feature_book', 'create_feature_book')
class FeatureBookViewTestCase(TestCase):
    """Test the Create Featured Book view."""

    fixtures = [
        "BookClub/tests/fixtures/default_users.json",
        "BookClub/tests/fixtures/default_clubs.json",
        "BookClub/tests/fixtures/default_memberships.json",
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
        self.url = reverse('edit_featured_books', kwargs={'club_url_name': self.club.club_url_name})
        self.url_private_club = reverse('edit_featured_books', kwargs={'club_url_name': self.private_club.club_url_name})
        
        ClubMembership.objects.create(user=self.owner, club=self.club, membership=ClubMembership.UserRoles.OWNER)
        ClubMembership.objects.create(user=self.moderator, club=self.club, membership=ClubMembership.UserRoles.MODERATOR)
        ClubMembership.objects.create(user=self.member, club=self.club, membership=ClubMembership.UserRoles.MEMBER)
        ClubMembership.objects.create(user=self.applicant, club=self.private_club, membership=ClubMembership.UserRoles.APPLICANT)
        ClubMembership.objects.create(user=self.owner, club=self.private_club, membership=ClubMembership.UserRoles.OWNER)

        self.data = {
            "book" : self.book.id,
            "reason" : 'A really good reason'
        }

    def test_feature_book_url(self):
        self.assertEqual(self.url, f'/club/{self.club.club_url_name}/featured/')

    def test_post_feature_book_redirects_when_not_logged_in(self):
        featured_book_count_before = FeaturedBooks.get_books(self.club).count()
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.post(self.url, self.data, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200, fetch_redirect_response=True)
        self.assertTemplateUsed(response, 'authentication/login.html')
        featured_book_count_after = FeaturedBooks.get_books(self.club).count()
        self.assertEqual(featured_book_count_before, featured_book_count_after)

    def test_get_feature_book_redirects_when_not_logged_in(self):
        featured_book_count_before = FeaturedBooks.get_books(self.club).count()
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200, fetch_redirect_response=True)
        self.assertTemplateUsed(response, 'authentication/login.html')
        featured_book_count_after = FeaturedBooks.get_books(self.club).count()
        self.assertEqual(featured_book_count_before, featured_book_count_after)

    '''Tests moderators and owners can see the feature book template'''

    def test_owner_can_see_feature_book_template(self):
        self.client.login(username=self.owner.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'clubs/edit_featured_books.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, FeatureBookForm))
        self.assertFalse(form.is_bound)
    
    def test_moderator_can_see_feature_book_template(self):
        self.client.login(username=self.moderator.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'clubs/edit_featured_books.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, FeatureBookForm))
        self.assertFalse(form.is_bound)

    '''Tests for users which cannot see the feature book form'''

    def test_member_cannot_see_feature_book_template(self):
        self.client.login(username=self.member.username, password='Password123')
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Only the owner or a moderator can feature books!')

    def test_applicant_cannot_see_feature_book_template(self):
        self.client.login(username=self.applicant.username, password='Password123')
        response = self.client.get(self.url_private_club, follow=True)
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'This club is private')

    '''Tests for users creating featured books'''

    def test_owner_can_feature_book(self):
        self.client.login(username=self.owner.username, password='Password123')
        before_count = FeaturedBooks.get_books(self.club).count()
        response = self.client.post(self.url, self.data, follow=True)
        self.assertEqual(response.status_code, 200)
        after_count = FeaturedBooks.get_books(self.club).count()
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Successfully featured book!')
        self.assertEqual(after_count, before_count + 1)
        self.assertTemplateUsed(response, 'clubs/club_dashboard.html')
        self.assertTrue(FeaturedBooks.objects.filter(club=self.club, book=self.book).exists())

    def test_moderator_can_feature_book(self):
        self.client.login(username=self.moderator.username, password='Password123')
        before_count = FeaturedBooks.get_books(self.club).count()
        response = self.client.post(self.url, self.data, follow=True)
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Successfully featured book!')
        after_count = FeaturedBooks.get_books(self.club).count()
        self.assertEqual(after_count, before_count + 1)
        self.assertTemplateUsed(response, 'clubs/club_dashboard.html')
        self.assertTrue(FeaturedBooks.objects.filter(club=self.club, book=self.book).exists())

    """Test for errors when creation is invalid"""

    def test_cannot_feature_book_twice(self):
        self.client.login(username=self.owner.username, password='Password123')
        FeaturedBooks.objects.create(club=self.club, book=self.book)
        before_count = FeaturedBooks.get_books(self.club).count()
        response = self.client.post(self.url, self.data, follow=True)
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Book is already featured!')
        after_count = FeaturedBooks.get_books(self.club).count()
        self.assertEqual(after_count, before_count)
        self.assertTrue(FeaturedBooks.objects.filter(club=self.club, book=self.book).exists())

    def test_cannot_feature_invalid_book(self):
        self.client.login(username=self.owner.username, password='Password123')
        before_count = FeaturedBooks.get_books(self.club).count()
        self.data['book'] = 123456
        response = self.client.post(self.url, self.data, follow=True)
        with self.assertRaises(ObjectDoesNotExist):
            FeaturedBooks.objects.get(id=123456).exists()
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'The data provided was invalid!')
        after_count = FeaturedBooks.get_books(self.club).count()
        self.assertEqual(after_count, before_count)
        self.assertFalse(FeaturedBooks.objects.filter(club=self.club, book=self.book).exists())

    def test_cannot_feature_book_for_invalid_club(self):
        self.client.login(username=self.owner.username, password='Password123')
        before_count = FeaturedBooks.get_books(self.club).count()
        url = reverse('edit_featured_books', kwargs={'club_url_name': 'some_random_name'})
        response = self.client.post(url, self.data, follow=True)
        with self.assertRaises(ObjectDoesNotExist):
            Club.objects.get(club_url_name="some_random_name").exists()
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Club not found or you are not a member of this club')
        after_count = FeaturedBooks.get_books(self.club).count()
        self.assertEqual(after_count, before_count)
        self.assertFalse(FeaturedBooks.objects.filter(club=self.club, book=self.book).exists())

    def test_form_invalid_for_feature_book(self):
        self.client.login(username=self.owner.username, password='Password123')
        data = {"reason" : 'A really good reason'}
        before_count = FeaturedBooks.get_books(self.club).count()
        response = self.client.post(self.url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'The data provided was invalid!')
        after_count = FeaturedBooks.get_books(self.club).count()
        self.assertEqual(after_count, before_count)
        self.assertFalse(FeaturedBooks.objects.filter(club=self.club, book=self.book).exists())
