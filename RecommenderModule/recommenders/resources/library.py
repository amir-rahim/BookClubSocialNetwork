import pandas as pd
from BookClub.models.book import Book

"""This class acts as a library to recover information about books and ratings."""
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

    """Get the ISBN value of all books the specified user has rated"""
    def get_all_books_rated_by_user(self, user_id):
        if (self.trainset == None):
            print("No trainset provided")
            return []
        else:
            user_inner_id = self.trainset.to_inner_uid(user_id)
            ratings_tuples = self.trainset.ur[user_inner_id]
            books = []
            for item_inner_id, rating in ratings_tuples:
                books.append(self.trainset.to_raw_iid(item_inner_id))
            return books

    """Get the rating the specified user made for the specified book"""
    def get_rating_from_user_and_book(self, user_id, book_isbn):
        if (self.trainset == None):
            print("No trainset provided")
            return None
        else:
            try:
                user_inner_id = self.trainset.to_inner_uid(user_id)
                item_inner_id = self.trainset.to_inner_iid(book_isbn)
                ratings_tuples = self.trainset.ur[user_inner_id]
                for iid, rating in ratings_tuples:
                    if (iid == item_inner_id):
                        return rating
                return None
            except:
                return None

    """Get all the ratings from the specified user, of books that are in the trainset, with a minimum rating value of {min_rating}"""
    def get_trainset_user_book_ratings(self, user_id, min_rating=0):
        items = self.get_all_books_rated_by_user(user_id)
        inner_items = []
        for item in items:
            try:
                inner_item = self.trainset.to_inner_iid(item)
                rating = self.get_rating_from_user_and_book(user_id, item)
                if (rating != None and rating >= min_rating):
                    inner_items.append((inner_item, rating))
            except:
                pass
        return inner_items