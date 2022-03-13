import pandas as pd
from BookClub.models.book import Book

"""This class acts as a library to recover information about a book"""
class Library:

    trainset = None

    def __init__(self, trainset=None):
        self.trainset = trainset

    """Get the title of the book, given its ISBN value"""
    def get_book_title(self, book_isbn):
        book = Book.objects.get(ISBN = book_isbn)
        return book.title

    """Get all the ratings values for the specified book"""
    def get_all_ratings_for_isbn(self, isbn):
        if (self.trainset == None):
            print("No trainset provided")
            return []
        else:
            item_inner_id = self.trainset.to_inner_iid(isbn)
            ratings_tuples = self.trainset.ir[item_inner_id]
            ratings = []
            for user_inner_id, rating in ratings_tuples:
                ratings.append(rating)
            return ratings
