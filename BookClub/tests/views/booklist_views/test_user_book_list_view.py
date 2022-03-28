"""Tests for Meeting Participants List View"""
from django.test import TestCase, tag
from django.urls import reverse
from django.utils import timezone

from BookClub.models import User, BookList
from BookClub.tests.helpers import LogInTester


@tag("booklist", "user_list")
class UserBookListViewTestCase(TestCase, LogInTester):
    fixtures = [
        'BookClub/tests/fixtures/default_users.json',
        'BookClub/tests/fixtures/default_books.json',
        'BookClub/tests/fixtures/booklists.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='johndoe')
        self.other_user = User.objects.get(pk=2)
        self.booklist = BookList.objects.get(pk=1)

        self.url = reverse('user_booklist', kwargs={'booklist_id': self.booklist.id})

    def test_url(self):
        self.assertEqual(self.url, f'/library/lists/{self.booklist.id}/')

    def test_get_template(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'booklists/booklist.html')

    def test_other_user_can_see_public_list(self):
        self.client.login(username=self.other_user.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'booklists/booklist.html')
        self.assertContains(response, "Classical Mythology")
        self.assertContains(response, "Mark P. O. Morford")
        self.assertContains(response, "The Greek Myths: The Complete and Definitive Edition")
        self.assertContains(response, "Robert Graves")

    def test_user_can_see_own_books_in_list(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'booklists/booklist.html')
        self.assertContains(response, "Classical Mythology")
        self.assertContains(response, "Mark P. O. Morford")
        self.assertContains(response, "The Greek Myths: The Complete and Definitive Edition")
        self.assertContains(response, "Robert Graves")

    def test_empty_book_list(self):
        self.client.login(username=self.user.username, password='Password123')
        booklist = BookList.objects.create(title='Booklist 1',
                                           description='Description 1',
                                           creator=self.user,
                                           created_on=timezone.now()
                                           )
        response = self.client.get(
            reverse('user_booklist', kwargs={'booklist_id': booklist.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'booklists/booklist.html')
        self.assertContains(response, "There are no books in this list.")
