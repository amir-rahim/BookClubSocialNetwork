"""This abstract class represents a model of recommender"""
class AbstractRecommender:

    """Train the recommender to recommend books, using the current or given data;
                parameters may contain a value for 'min_ratings_threshold', 'min_support' and 'model_function_name' """
    def train(self, trainset=None, parameters={}):
        raise NotImplementedError("Attempting to use abstract method from BaseRecommender super class.")

    """Train the recommender to recommend books, using the current or given data, and save it to be re-used as default;
            parameters may contain a value for 'min_ratings_threshold', 'min_support' and 'model_function_name' """
    def train_and_save(self, trainset=None, parameters={}):
        raise NotImplementedError("Attempting to use abstract method from BaseRecommender super class.")

    """Get the recommended books (up to 10) given a specified user_id, from all of the user's positively (> 6/10) rated books"""
    def get_recommendations(self, user_id):
        raise NotImplementedError("Attempting to use abstract method from BaseRecommender super class.")