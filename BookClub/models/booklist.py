from django.db import models
from BookClub.models import User, Book



class BookList(models.Model):
    title = models.CharField(unique=False, blank=False, max_length=120)
    description = models.CharField(unique=False, blank=True, max_length=240)
    creator = models.ForeignKey(User, blank= False, null = False, on_delete=models.CASCADE)
    books = models.ManyToManyField(Book)
    created_on = models.DateTimeField(auto_now_add=True)

