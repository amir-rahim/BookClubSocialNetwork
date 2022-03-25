from RecommenderModule.recommenders.resources.abstract_recommender import AbstractRecommender
from RecommenderModule.recommenders.resources.content_based_recommender_methods import ContentBasedRecommenderMethods

"""This class allows the developer to recommend books to a user, based on content similarity between books"""
class ContentBasedRecommender(AbstractRecommender):

    content_based_methods = None

    def __init__(self):
        self.content_based_methods = ContentBasedRecommenderMethods()

    """Train the recommender to recommend books, using the current or given data;
                parameters may contain a value for 'using_publication_year' """
    def fit(self, trainset=None, parameters={}):
        self.content_based_methods = ContentBasedRecommenderMethods(trainset=trainset, retraining=True, parameters=parameters)

    """Train the recommender to recommend books, using the current or given data, and save it to be re-used as default;
                parameters may contain a value for 'using_publication_year' """
    def fit_and_save(self, trainset=None, parameters={}):
        self.content_based_methods = ContentBasedRecommenderMethods(trainset=trainset, retraining_and_saving=True, parameters=parameters)

    """Get the recommended books (up to 10) given a specified user_id, from all of the user's positively (> 6/10) rated books"""
    def get_user_recommendations(self, user_id):
        return self.content_based_methods.get_recommendations_positive_ratings_only_from_user_id(user_id, min_rating=6)

    """Get the recommended books (up to 10) given a specified club_id, from all of the club's members' positively (> 6/10) rated books"""
    def get_club_recommendations(self, club_url_name):
        return self.content_based_methods.get_recommendations_positive_ratings_only_from_club_url_name(club_url_name, min_rating=6)
