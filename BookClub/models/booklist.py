from django.db import models
from BookClub.models import User, Book



class BookList(models.Model):
    creator = models.ForeignKey(User,blank= False, null = False, on_delete= models.CASCADE)
    books = models.ManyToManyField(Book, on_delete=models.RESTRICT, blank=True, unique=True)
    created_on = models.DateTimeField(auto_now_add=True)