from django.db import models
from BookClub.models import User, Book
from django.urls import reverse


class BookList(models.Model):
    title = models.CharField(unique=False, blank=False, max_length=120)
    description = models.CharField(unique=False, blank=True, max_length=240)
    creator = models.ForeignKey(User, blank= False, null = False, on_delete=models.CASCADE)
    books = models.ManyToManyField(Book, blank=True)
    created_on = models.DateField(auto_now_add=True)

    def get_absolute_url(self):
        return reverse('booklists_list', kwargs = {'username': self.creator.username})

    def get_books(self):
        return self.books.all()

