from django.test import TestCase, tag
from django.urls import reverse
from BookClub.models import User, Book


@tag("views", "books", "library_books")
class LibraryBooksViewTestCase(TestCase):
    """Tests of the Library Books view."""

    fixtures = [
        'BookClub/tests/fixtures/default_users.json',
        'BookClub/tests/fixtures/default_books.json',
    ]

    def setUp(self):
        self.url = reverse('library_books')
        self.user = User.objects.get(username="johndoe")

    def test_books_url(self):
        self.assertEqual(self.url, '/library/books/')

    def test_get_dashboard_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'library/library_books.html')

    def test_get_dashboard_logged_in(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'library/library_books.html')

    def test_no_books(self):
        Book.objects.all().delete()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'library/library_books.html')
        books = list(response.context['books'])
        self.assertEqual(len(books), 0)
        self.assertContains(response, "There are no books matching this search.")

    def test_books_show(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'library/library_books.html')
        books = list(response.context['books'])
        self.assertEqual(len(books), 4)

    def test_book_details_show(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'library/library_books.html')
        self.assertContains(response, "Classical Mythology")
        self.assertContains(response, "Mark P. O. Morford")
        self.assertContains(response, "Oxford University Press")
        self.assertContains(response, "http://images.amazon.com/images/P/0195153448.01.MZZZZZZZ.jpg")