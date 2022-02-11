import datetime
from django.forms import ValidationError
from BookClub.models import Book
from django.db import models
from django.test import TestCase


class BookTestCase(TestCase):
    
    fixtures=[
        'BookClub/tests/fixtures/books.json'
    ]
    
    def setUp(self):
        self.book = Book.objects.get(pk=1)
        self.data={
            "title":"TestBook",
            
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
        self.book.title=""
        self.assertInvalid()
        
    def test_ISBN_cannot_be_blank(self):
        self.book.ISBN = ""
        self.assertInvalid()
        
    def test_author_cannot_be_blank(self):
        self.book.author=""
        self.assertInvalid()
        
    def test_publicationYear_cannot_be_blank(self):
        self.book.publicationYear=""
        self.assertInvalid()
    
    def test_publisher_cannot_be_blank(self):
        self.book.publisher=""
        self.assertInvalid()
        
    def test_ImageS_can_be_blank(self):
        self.book.imageS=""
        self.assertValid()
        
    def test_ImageM_can_be_blank(self):
        self.book.imageM=""
        self.assertValid()
        
    def test_ImageL_can_be_blank(self):
        self.book.imageL=""
        self.assertValid()
        
    def test_get_publication_year(self):
        year = self.book.getPublicationYear()
        self.assertEqual(2002, year)
        
    def test_str_returns_title(self):
        title = str(self.book)
        self.assertEqual(self.book.title, title)
        