from BookClub.recommender_module.recommenders.popular_books_recommender import PopularBooksRecommender
from BookClub.recommender_module.recommenders.resources.popular_books_recommender_methods import PopularBooksMethods
from BookClub.models.review import BookReview


"""Get the 10 most popular books recommended to the user (that the user has not read yet).
    Returns a list of ISBN numbers."""
def get_popularity_recommendations(user):
    user_read_books = get_user_read_books(user)
    # Import Popular Books recommender
    popular_books = PopularBooksRecommender()
    recommended_books = popular_books.get_recommendations_from_average_and_median(user_read_books=user_read_books)
    return recommended_books

"""Retrain the popularity recommender with the current data."""
def retrain_popularity_recommender():
    PopularBooksMethods(retraining_and_saving=True)

"""Get a list of all books that the user has read."""
def get_user_read_books(user):
    try:
        user_reviews = BookReview.objects.get(user=user)
    except:
        user_reviews = []
    isbn_list = []
    for review in user_reviews:
        isbn_list.append(review.book.ISBN)
    return isbn_list

"""Get (up to) 10 book recommendations, from books the user has rated."""
def get_item_based_recommendations(user, positive_ratings_only=True):
    user_read_books = self.get_user_read_books(user)

"""Retrain the item-based recommender with the current data"""
def retrain_item_based_recommender():
    pass
