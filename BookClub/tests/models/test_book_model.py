from genericpath import getsize
from django.forms import ValidationError
from django.test import TestCase, tag

from BookClub.models import Book


@tag('models', 'book')
class BookTestCase(TestCase):
    fixtures = [
        'BookClub/tests/fixtures/default_books.json'
    ]

    def setUp(self):
        self.book = Book.objects.get(pk=1)
        self.small = "http://images.amazon.com/images/P/0195153448.01.THUMBZZZ.jpg"
        self.medium = "http://images.amazon.com/images/P/0195153448.01.MZZZZZZZ.jpg"
        self.large = "http://images.amazon.com/images/P/0195153448.01.LZZZZZZZ.jpg"
        self.data = {
            "title": "TestBook"
        }

    def assertValid(self):
        try:
            self.book.full_clean()
        except(ValidationError):
            self.fail('Book should be valid')

    def assertInvalid(self):
        with self.assertRaises(Exception):
            self.book.full_clean()

    def test_valid_info(self):
        self.assertValid()

    def testTitleCannotBeBlank(self):
        self.book.title = ""
        self.assertInvalid()

    def test_ISBN_cannot_be_blank(self):
        self.book.ISBN = ""
        self.assertInvalid()

    def test_author_cannot_be_blank(self):
        self.book.author = ""
        self.assertInvalid()

    def test_publicationYear_cannot_be_blank(self):
        self.book.publicationYear = ""
        self.assertInvalid()

    def test_publisher_cannot_be_blank(self):
        self.book.publisher = ""
        self.assertInvalid()

    def test_ImageS_can_be_blank(self):
        self.book.imageS = ""
        self.assertValid()

    def test_ImageM_can_be_blank(self):
        self.book.imageM = ""
        self.assertValid()

    def test_ImageL_can_be_blank(self):
        self.book.imageL = ""
        self.assertValid()

    def test_get_publication_year(self):
        year = self.book.getPublicationYear()
        self.assertEqual(2002, year)

    def test_str_returns_title(self):
        title = str(self.book)
        self.assertEqual(self.book.title, title)

    def test_get_absolute_url(self):
        url = self.book.get_absolute_url()
        correct_url = '/library/books/1/'
        self.assertEqual(url, correct_url)

    def test_get_s_size(self):
        self.assertEqual(1378, self.book.get_s_size())

    def test_get_m_size(self):
        self.assertEqual(3978, self.book.get_m_size())

    def test_get_l_size(self):
        self.assertEqual(31578, self.book.get_l_size())

    def test_get_short_description(self):
        self.assertEqual(self.book.get_short_description(), '"Classical Mythology" by Mark P. O. Morford')
