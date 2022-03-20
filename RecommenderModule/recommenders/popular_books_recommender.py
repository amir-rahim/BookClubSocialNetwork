from RecommenderModule.recommenders.resources.popular_books_recommender_methods import PopularBooksMethods
from RecommenderModule.recommenders.resources.abstract_recommender import AbstractRecommender
from RecommenderModule.recommenders.resources.library import Library

"""This class allows the developer to recommend the most popular books to a user"""
class PopularBooksRecommender(AbstractRecommender):

    popular_books_methods = None
    trainset = None

    """Train the recommender to recommend books, using the current or given data;
        parameters may contain a value for 'min_ratings_threshold' """
    def fit(self, trainset=None, parameters={}):
        if "min_ratings_threshold" in parameters.keys():
            self.popular_books_methods = PopularBooksMethods(min_ratings_threshold=parameters["min_ratings_threshold"], trainset=trainset, retraining=True)
        else:
            self.popular_books_methods = PopularBooksMethods(trainset=trainset, retraining=True)

    """Train the recommender to recommend books, using the current or given data, and save it to be re-used as default;
        parameters may contain a value for 'min_ratings_threshold' """
    def fit_and_save(self, trainset=None, parameters={}):
        if "min_ratings_threshold" in parameters.keys():
            self.popular_books_methods = PopularBooksMethods(min_ratings_threshold=parameters["min_ratings_threshold"], trainset=trainset, retraining_and_saving=True)
        else:
            self.popular_books_methods = PopularBooksMethods(trainset=trainset, retraining_and_saving=True)

    """Get most popular books (up to 10) according to their average rating, that the user has not read yet"""
    def get_user_recommendations(self, user_id):
        library = Library(self.trainset)
        user_read_books = library.get_list_of_books_rated_by_user(user_id)
        if self.popular_books_methods is None:
            self.popular_books_methods = PopularBooksMethods()
        return self.popular_books_methods.get_recommendations_from_median(read_books=user_read_books)

    """Get most popular books (up to 10) according to their average rating, that no member of the club has read yet"""
    def get_club_recommendations(self, club_url_name):
        library = Library(self.trainset)
        club_read_books = library.get_list_of_books_rated_by_club(club_url_name)
        if self.popular_books_methods is None:
            self.popular_books_methods = PopularBooksMethods()
        return self.popular_books_methods.get_recommendations_from_median(read_books=club_read_books)
