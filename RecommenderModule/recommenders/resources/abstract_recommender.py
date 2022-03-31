"""This abstract class represents a model of recommender"""
class AbstractRecommender:

    """Train the recommender to recommend books, using the current or given data;
                parameters may contain a value for 'min_ratings_threshold', 'min_support' and 'model_function_name' """
    def fit(self, trainset=None, parameters={}):
        raise NotImplementedError("Attempting to use abstract method from BaseRecommender super class.")

    """Train the recommender to recommend books, using the current or given data, and save it to be re-used as default;
            parameters may contain a value for 'min_ratings_threshold', 'min_support' and 'model_function_name' """
    def fit_and_save(self, trainset=None, parameters={}):
        raise NotImplementedError("Attempting to use abstract method from BaseRecommender super class.")

    """Get the recommended books (up to 10) given a specified user_id, from all of the user's positively (> 6/10) rated books"""
    def get_user_recommendations(self, user_id):
        raise NotImplementedError("Attempting to use abstract method from BaseRecommender super class.")

    """Get the recommended books (up to 10) given a specified club_url_name, from all of the club's members' positively (> 6/10) rated books"""
    def get_club_recommendations(self, club_url_name):
        raise NotImplementedError("Attempting to use abstract method from BaseRecommender super class.")

    """Get the number of books that can be recommender to the user, using this recommender algorithm"""
    def get_number_of_recommendable_books(self):
        raise NotImplementedError("Attempting to use abstract method from BaseRecommender super class.")
