from datetime import datetime
from django.db import models


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

    def __str__(self):
        return self.title

    def getPublicationYear(self):
        date = self.publicationYear
        return date.year
