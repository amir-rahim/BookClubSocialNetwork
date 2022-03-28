from django.db import models
from django.urls import reverse
import urllib


class Book(models.Model):
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
