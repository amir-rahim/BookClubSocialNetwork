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
      
    def get_delete_url(self):
        return reverse('delete_booklist', kwargs = {'username' : self.creator.username, 'list_id' : self.pk})

    def __str__(self):
        return f"Book List '{self.title}' with {self.books.count()} titles"
      
    def get_books(self):
        return self.books.all()

    def add_book(self, book):
        self.books.add(book)

    def remove_book(self, book):
        self.books.remove(book)
