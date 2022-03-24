from django.db import models
from django.urls import reverse

from BookClub.models import Book, UserCreatedObject


class BookList(UserCreatedObject):
    title = models.CharField(unique=False, blank=False, max_length=120)
    description = models.CharField(unique=False, blank=True, max_length=240)
    books = models.ManyToManyField(Book, blank=True)

    def get_absolute_url(self):
        return reverse('user_booklist', kwargs={'username': self.creator.username, 'booklist_id': self.pk})

    def get_delete_url(self):
        return reverse('delete_booklist', kwargs={'username': self.creator.username, 'list_id': self.pk})

    def __str__(self):
        return f"Book List '{self.title}' with {self.books.count()} titles"

    def get_books(self):
        return self.books.all()

    def add_book(self, book):
        self.books.add(book)

    def remove_book(self, book):
        self.books.remove(book)
