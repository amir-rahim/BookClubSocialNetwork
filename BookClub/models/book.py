"""Book model."""
from django.db import models
from django.urls import reverse
import urllib


class Book(models.Model):
    """Model for book objects for the library.
    
    Attributes:
        title: A string that contains the title of the Book.
        ISBN: A string that contains the ISBN of the Book.
        author: A string that contains the author of the Book.
        publicationYear: A Date that the Book was published on.
        publisher: A string that takes the name of the Book's publisher.
        imageS: A URL of the Book's cover, small size.
        imageM: A URL of the Book's cover, medium size.
        imageL: A URL of the Book's cover, large size.
    """
    class Meta:
        ordering = ['-id']

    title = models.TextField(unique=False, blank=False)
    ISBN = models.CharField(unique=True, max_length=15, blank=False)
    author = models.TextField(unique=False, blank=False, max_length=100)
    publicationYear = models.DateField(unique=False, blank=False)
    publisher = models.TextField(unique=False, blank=False)
    imageS = models.URLField(unique=False, blank=True)
    imageM = models.URLField(unique=False, blank=True)
    imageL = models.URLField(unique=False, blank=True)

    def get_absolute_url(self):
        return reverse('book_view', kwargs={'book_id': self.pk})

    def __str__(self):
        return self.title

    def getPublicationYear(self):
        date = self.publicationYear
        return date.year

    def get_s_size(self):
        file = urllib.request.urlopen(self.imageS)
        size = file.headers.get("content-length")
        file.close()
        return int(size)

    def get_m_size(self):
        file = urllib.request.urlopen(self.imageM)
        size = file.headers.get("content-length")
        file.close()
        return int(size)

    def get_l_size(self):
        file = urllib.request.urlopen(self.imageL)
        size = file.headers.get("content-length")
        file.close()
        return int(size)

    def get_short_description(self):
        return f'"{self.title}" by {self.author}'
