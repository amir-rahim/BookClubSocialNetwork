import pandas as pd
from BookClub.models import Book, User, BookReview

"""This class acts as a library to recover information about books and ratings."""
class Library:

    trainset = None

    def __init__(self, trainset=None):
        self.trainset = trainset

    """Get all the ratings values for the specified book"""
    def get_all_ratings_for_isbn_from_trainset(self, isbn):
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
        if self.trainset is None: # Get from Django

            try:
                user = User.objects.get(username=user_id)
                user_reviews = BookReview.objects.filter(user=user)
                books = []
                for review in user_reviews:
                    books.append(review.book.ISBN)
                return books
            except:
                return []

        else:

            try:
                user_inner_id = self.trainset.to_inner_uid(user_id)
                ratings_tuples = self.trainset.ur[user_inner_id]
                books = []
                for item_inner_id, rating in ratings_tuples:
                    books.append(self.trainset.to_raw_iid(item_inner_id))
                return books
            except:
                return []

    """Get the rating the specified user made for the specified book"""
    def get_rating_from_user_and_book(self, user_id, book_isbn):
        if (self.trainset == None): # Get from Django

            try:
                user = User.objects.get(username=user_id)
                book = Book.objects.get(ISBN=book_isbn)
                review = BookReview.objects.get(user=user, book=book)
                return int(review.rating)
            except:
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
