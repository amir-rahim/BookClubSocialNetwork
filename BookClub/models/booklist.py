"""Book list model."""
from django.db import models
from django.urls import reverse

from BookClub.models import Book, UserCreatedObject


class BookList(UserCreatedObject):
    """A Book List to allow the user to store and categorise Books.
    
    Attributes:
        title: A string that contains the title of the Book List.
        description: A string that describes the Book List; created by the User.
        books: A list of Books in the Book List.    
    """
    title = models.CharField(unique=False, blank=False, max_length=120)
    description = models.CharField(unique=False, blank=True, max_length=240)
    books = models.ManyToManyField(Book, blank=True)

    def get_absolute_url(self):
        return reverse('user_booklist', kwargs={'booklist_id': self.pk})

    def get_delete_url(self):
        return reverse('delete_booklist', kwargs={'booklist_id': self.pk})

    def __str__(self):
        return f"Book List '{self.title}' with {self.books.count()} titles"

    def get_delete_str(self):
        return self.__str__()

    def get_books(self):
        return self.books.all()

    def add_book(self, book):
        self.books.add(book)

    def remove_book(self, book):
        self.books.remove(book)

    def get_short_contents(self):
        return_str = ''
        for book in self.books.all().order_by('pk'):
            return_str += f'{book.get_short_description()}; '

        if len(return_str) > 75:
            return_str = return_str[:72] + '...'
        return return_str
