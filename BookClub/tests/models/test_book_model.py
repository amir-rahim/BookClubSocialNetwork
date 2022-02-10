from BookClub.models import Book
from django.db import models



class BookTestCase(models.Model):
    
    fixtures=[
        'BookClub/tests/fixtures/books.json'
    ]
    
    def setUp(self):
        self.book = Book.objects.get(pk=1)