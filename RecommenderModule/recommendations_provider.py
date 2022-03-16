from RecommenderModule.recommenders.popular_books_recommender import PopularBooksRecommender
from RecommenderModule.recommenders.item_based_recommender import ItemBasedRecommender

"""Get the 10 most popular books recommended to the user (that the user has not read yet).
    Returns a list of ISBN numbers."""
def get_popularity_recommendations(user_id):
    popularity_recommender = PopularBooksRecommender()
    recommended_books = popularity_recommender.get_recommendations(user_id)
    return recommended_books

"""Retrain the popularity recommender with the current data."""
def retrain_popularity_recommender(min_ratings_threshold=300):
    popularity_recommender = PopularBooksRecommender()
    popularity_recommender.train_and_save(parameters={"min_ratings_threshold": min_ratings_threshold})

"""Get (up to) 10 book recommendations, from books the user has rated."""
def get_personalised_recommendations(user_id):
    item_based_recommender = ItemBasedRecommender()
    recommended_books = item_based_recommender.get_recommendations(user_id)
    return recommended_books

"""Retrain the item-based recommender with the current data;
    parameters may contain a value for 'min_ratings_threshold', 'min_support' and 'model_function_name' """
def retrain_item_based_recommender(parameters={}):
    item_based_recommender = ItemBasedRecommender()
    item_based_recommender.train_and_save(parameters=parameters)
