import pandas as pd
from BookClub.models.book import Book

"""This class acts as a library to recover information about a book"""
class Library:

    """Get the title of the book, given its ISBN value"""
    def get_book_title(self, book_isbn):
        book = Book.objects.get(ISBN = book_isbn)
        return book.title
