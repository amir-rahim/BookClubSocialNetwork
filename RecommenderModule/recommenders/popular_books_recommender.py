from RecommenderModule.recommenders.resources.popular_books_recommender_methods import PopularBooksMethods
from RecommenderModule.recommenders.resources.abstract_recommender import AbstractRecommender
from RecommenderModule.recommenders.resources.library import Library

"""This class allows the developer to recommend the most popular books to a user"""
class PopularBooksRecommender(AbstractRecommender):

    popular_books_methods = None
    trainset = None

    def __init__(self, print_status=False):
        self.print_status = print_status

    """Train the recommender to recommend books, using the current or given data;
        parameters may contain a value for 'min_ratings_threshold' and 'ranking_method' """
    def fit(self, trainset=None, parameters={}):
            self.popular_books_methods = PopularBooksMethods(trainset=trainset, retraining=True, parameters=parameters, print_status=self.print_status)

    """Train the recommender to recommend books, using the current or given data, and save it to be re-used as default;
        parameters may contain a value for 'min_ratings_threshold' and 'rankin_method' """
    def fit_and_save(self, trainset=None, parameters={}):
            self.popular_books_methods = PopularBooksMethods(trainset=trainset, retraining_and_saving=True, parameters=parameters, print_status=self.print_status)

    """Get most popular books (up to 10) according to their average rating, that the user has not read yet"""
    def get_user_recommendations(self, user_id):
        library = Library(self.trainset)
        user_read_books = library.get_list_of_books_rated_by_user(user_id)
        if self.popular_books_methods is None:
            self.popular_books_methods = PopularBooksMethods(print_status=self.print_status)
        return self.popular_books_methods.get_recommendations(read_books=user_read_books)

    """Get most popular books (up to 10) according to their average rating, that no member of the club has read yet"""
    def get_club_recommendations(self, club_url_name):
        library = Library(self.trainset)
        club_read_books = library.get_list_of_books_rated_by_club(club_url_name)
        if self.popular_books_methods is None:
            self.popular_books_methods = PopularBooksMethods(print_status=self.print_status)
        return self.popular_books_methods.get_recommendations(read_books=club_read_books)

    """Get the number of books that can be recommender to the user, using this recommender algorithm"""
    def get_number_of_recommendable_books(self):
        if self.popular_books_methods is None:
            self.popular_books_methods = PopularBooksMethods(print_status=self.print_status)
        return self.popular_books_methods.get_number_of_recommendable_books()
