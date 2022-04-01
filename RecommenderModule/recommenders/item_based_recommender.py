from RecommenderModule.recommenders.resources.item_based_collaborative_filtering_methods import ItemBasedCollaborativeFilteringMethods
from RecommenderModule.recommenders.resources.abstract_recommender import AbstractRecommender

"""This class allows the developer to recommend books to a user, similar to the user's rated books"""
class ItemBasedRecommender(AbstractRecommender):

    item_based_methods = None

    def __init__(self):
        self.item_based_methods = ItemBasedCollaborativeFilteringMethods()

    """Train the recommender to recommend books, using the current or given data;
            parameters may contain a value for 'min_ratings_threshold', 'min_support' and 'model_function_name' """
    def fit(self, trainset=None, parameters={}):
        self.item_based_methods = ItemBasedCollaborativeFilteringMethods(trainset=trainset, retraining=True, parameters=parameters)

    """Train the recommender to recommend books, using the current or given data, and save it to be re-used as default;
            parameters may contain a value for 'min_ratings_threshold', 'min_support' and 'model_function_name' """
    def fit_and_save(self, trainset=None, parameters={}):
        self.item_based_methods = ItemBasedCollaborativeFilteringMethods(trainset=trainset, retraining_and_saving=True, parameters=parameters)

    """Get the recommended books (up to 10) given a specified user_id, from all of the user's positively (> 6/10) rated books"""
    def get_user_recommendations(self, user_id):
        return self.item_based_methods.get_recommendations_positive_ratings_only_from_user_id(user_id, min_rating=6)

    """Get the recommended books (up to 10) given a specified club_id, from all of the club's members' positively (> 6/10) rated books"""
    def get_club_recommendations(self, club_url_name):
        return self.item_based_methods.get_recommendations_positive_ratings_only_from_club_url_name(club_url_name, min_rating=6)

    """Get the number of books that can be recommender to the user, using this recommender algorithm"""
    def get_number_of_recommendable_books(self):
        return self.item_based_methods.trainset.n_items
