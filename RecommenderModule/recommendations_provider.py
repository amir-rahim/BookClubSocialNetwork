from RecommenderModule.recommenders.popular_books_recommender import PopularBooksRecommender
from RecommenderModule.recommenders.resources.popular_books_recommender_methods import PopularBooksMethods
from RecommenderModule.recommenders.item_based_recommender import ItemBasedRecommender
from RecommenderModule.recommenders.resources.item_based_collaborative_filtering_methods import ItemBasedCollaborativeFilteringMethods
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
def retrain_popularity_recommender(min_ratings_threshold=100):
    PopularBooksMethods(retraining_and_saving=True, min_ratings_threshold=min_ratings_threshold)

"""Get a list of all books that the user has read."""
def get_user_read_books(user):
    try:
        user_reviews = BookReview.objects.filter(user=user)
    except:
        user_reviews = []
    isbn_list = []
    for review in user_reviews:
        isbn_list.append(review.book.ISBN)
    return isbn_list

"""Get (up to) 10 book recommendations, from books the user has rated."""
def get_item_based_recommendations(user, positive_ratings_only=True):
    item_based = ItemBasedRecommender()
    if positive_ratings_only:
        recommended_books = item_based.get_recommendations_positive_ratings_only_from_user_id(user.username)
    else:
        recommended_books = item_based.get_recommendations_all_ratings_from_user_id(user.username)
    return recommended_books

"""Retrain the item-based recommender with the current data"""
def retrain_item_based_recommender(min_ratings_threshold=15, min_support=5):
    ItemBasedCollaborativeFilteringMethods(retraining_and_saving=True, filtering_min_ratings_threshold=min_ratings_threshold, min_support=min_support)
