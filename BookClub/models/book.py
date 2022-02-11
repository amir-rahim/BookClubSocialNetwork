

from datetime import datetime
from django.db import models

class Book(models.Model):
    
    title = models.CharField(unique=False, max_length=200, blank=False)
    ISBN = models.CharField(unique=True, max_length=15,blank=False)
    author = models.CharField(unique=False, blank=False, max_length=100)
    publicationYear = models.DateField(unique=False, blank=False)
    publisher = models.CharField(unique=False, blank=False, max_length=100)
    imageS = models.URLField(unique=False, blank=True)
    imageM = models.URLField(unique=False, blank=True)
    imageL = models.URLField(unique=False, blank=True)
    
    def __str__(self):
        return self.title
    
    def getPublicationYear(self):
        date = self.publicationYear
        return date.year