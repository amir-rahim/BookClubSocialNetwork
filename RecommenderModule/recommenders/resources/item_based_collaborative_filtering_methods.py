from RecommenderModule.recommenders.resources.data_provider import DataProvider
from RecommenderModule.recommenders.resources.library import Library
from surprise import KNNBasic
from collections import defaultdict
from operator import itemgetter
import math
import joblib

"""This class provides the developer with methods to recommend books to a user, similar to the user's rated books"""
class ItemBasedCollaborativeFilteringMethods:

    path_to_model = "RecommenderModule/recommenders/resources/item_based_model"
    data_provider = None
    trainset = None
    similarities_matrix = None
    library = None

    min_ratings_threshold = 15
    min_support = 5
    model_function_name = 'pearson_baseline'

    def __init__(self, parameters={}, retraining=False, retraining_and_saving=False, trainset=None, print_status=True):
        self.print_status = print_status
        self.initialise_parameters(parameters)
        self.library = Library(trainset=trainset)
        if (trainset == None):
            if (retraining or retraining_and_saving):
                self.build_trainset()
                self.train_model()
                if (retraining_and_saving):
                    self.save_model()
            else:
                try:
                    self.import_model()
                except:
                    self.__init__(parameters=parameters, retraining_and_saving=True)
        else: # trainset != None
            self.trainset = trainset
            self.train_model()


    """Store the values of the parameters into class attributes"""
    def initialise_parameters(self, parameters):
        if "min_ratings_threshold" in parameters.keys():
            self.min_ratings_threshold = parameters["min_ratings_threshold"]
        if "min_support" in parameters.keys():
            self.min_support = parameters["min_support"]
        if "model_function_name" in parameters.keys():
            self.model_function_name = parameters["model_function_name"]

    """Build the filtered ratings trainset, with only books having at least {filtering_min_ratings_threshold} ratings"""
    def build_trainset(self):
        if self.data_provider is None:
            self.data_provider = DataProvider(filtering_min_ratings_threshold=self.min_ratings_threshold)
        self.trainset = self.data_provider.get_filtered_ratings_trainset()

    """Train the KNN model on the defined trainset and compute the associated similarities matrix"""
    def train_model(self):
        sim_options = {
            'name': self.model_function_name,
            'user_based': False,
            'min_support': self.min_support
            }
        model = KNNBasic(sim_options=sim_options, verbose=self.print_status)
        model.fit(self.trainset)
        self.similarities_matrix = model.sim

    """Save the trainset and the similarities_matrix as .sav files, using the joblib library."""
    def save_model(self):
        joblib.dump(self.trainset, f"{self.path_to_model}/trainset.sav")
        joblib.dump(self.similarities_matrix, f"{self.path_to_model}/similarities_matrix.sav")

    """Import the trainset and the similarities_matrix from .sav files, using the joblib library."""
    def import_model(self):
        self.trainset = joblib.load(f"{self.path_to_model}/trainset.sav")
        self.similarities_matrix = joblib.load(f"{self.path_to_model}/similarities_matrix.sav")

    """Get the recommended books (up to 10) given a specified user_id, from all of the user's rated books"""
    def get_recommendations_all_ratings_from_user_id(self, user_id):
        raw_ratings = self.library.get_all_ratings_by_user(user_id)
        inner_ratings = self.get_inner_ratings_from_raw_ratings(raw_ratings)
        recommendations = self.get_recommendations_from_inner_ratings(inner_ratings)
        return recommendations

    """Get the recommended books (up to 10) given a specified user_id, from all of the user's positively (> 6/10) rated books"""
    def get_recommendations_positive_ratings_only_from_user_id(self, user_id, min_rating=6):
        raw_ratings = self.library.get_all_ratings_by_user(user_id)
        inner_ratings = self.get_inner_ratings_from_raw_ratings(raw_ratings)
        positive_inner_ratings = self.get_inner_ratings_from_raw_ratings(raw_ratings, min_rating=min_rating)
        recommendations = self.get_recommendations_from_inner_ratings(positive_inner_ratings, all_books_rated=inner_ratings)
        return recommendations

    """Extract the inner ids of the ratings passed in the raw_ratings argument,for books with a minimum rating value of {min_rating}"""
    def get_inner_ratings_from_raw_ratings(self, raw_ratings, min_rating=0):
        inner_ratings = []
        for book_isbn, rating in raw_ratings:
            try:
                inner_item = self.trainset.to_inner_iid(book_isbn)
                if rating >= min_rating:
                    inner_ratings.append((inner_item, rating))
            except:
                pass
        return inner_ratings

    """Get recommendations from trainset, corresponding similarities matrix and a list of ratings
        as inner ratings (from similarities matrix)"""
    def get_recommendations_from_inner_ratings(self, ratings, all_books_rated=None):

        # Define all books rated (read) by the user
        if all_books_rated == None:
            all_books_rated = ratings

        # Weigh items by rating
        candidates = defaultdict(float)
        for item_id, rating in ratings:
            similarity_row = self.similarities_matrix[item_id]
            for inner_id, score in enumerate(similarity_row):
                candidates[inner_id] += score * (rating / 10.0)

        # Get top-rated items from similar users
        final_recommendations = []
        all_books_rated_isbn = [rating[0] for rating in all_books_rated]
        for item_id, rating_sum in sorted(candidates.items(), key=itemgetter(1), reverse=True):
            # Check if user has already read the book, and only recommend the book if it has some similarity
            if (not item_id in all_books_rated_isbn) and (not math.isnan(rating_sum)) and rating_sum != 0:
                try:
                    book_isbn = self.trainset.to_raw_iid(item_id)
                    #print(book_isbn, rating_sum)
                    final_recommendations.append(book_isbn)
                    if (len(final_recommendations) >= 10): # Get the top 10 recommendations
                        break
                except:
                    pass

        return final_recommendations

    """Get the recommended books (up to 10) given a specified club_url_name, from all of the club's members' positively (> 6/10) rated books"""
    def get_recommendations_positive_ratings_only_from_club_url_name(self, club_url_name, min_rating=6):
        raw_ratings = self.library.get_all_ratings_by_club(club_url_name)
        inner_ratings = self.get_inner_ratings_from_raw_ratings(raw_ratings)
        positive_inner_ratings = self.get_inner_ratings_from_raw_ratings(raw_ratings, min_rating=min_rating)
        recommendations = self.get_recommendations_from_inner_ratings(positive_inner_ratings, all_books_rated=inner_ratings)
        return recommendations