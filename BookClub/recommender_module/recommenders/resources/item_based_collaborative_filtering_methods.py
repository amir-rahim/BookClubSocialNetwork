from BookClub.recommender_module.recommenders.resources.data_provider import DataProvider
from BookClub.recommender_module.recommenders.resources.library import Library
from surprise import KNNBasic
from collections import defaultdict
from operator import itemgetter
import math
import joblib

"""This class provides the developer with methods to recommend books to a user, similar to the user's rated books"""
class ItemBasedCollaborativeFilteringMethods:

    data_provider = None
    trainset = None
    similarities_matrix = None

    def __init__(self, filtering_min_ratings_threshold=15, retraining=False, retraining_and_saving=False):
        if (retraining or retraining_and_saving):
            self.build_trainset(filtering_min_ratings_threshold)
            self.train_model()
            if (retraining_and_saving):
                self.save_model()
        else:
            try:
                self.import_model()
            except:
                self.__init__(filtering_min_ratings_threshold=filtering_min_ratings_threshold, retraining_and_saving=True)


    """Build the filtered ratings trainset, with only books having at least {filtering_min_ratings_threshold} ratings"""
    def build_trainset(self, filtering_min_ratings_threshold):
        self.data_provider = DataProvider(filtering_min_ratings_threshold=filtering_min_ratings_threshold)
        self.trainset = self.data_provider.get_filtered_ratings_trainset()

    """Train the KNN model on the defined trainset and compute the associated similarities matrix"""
    def train_model(self):
        sim_options = {
            'name': 'pearson',
            'user_based': False,
            'min_support': 5
            }
        model = KNNBasic(sim_options=sim_options)
        model.fit(self.trainset)
        self.similarities_matrix = model.sim

    """Save the trainset and the similarities_matrix as .sav files, using the joblib library."""
    def save_model(self):
        joblib.dump(self.trainset, "BookClub/recommender_module/recommenders/resources/item_based_model/trainset.sav")
        joblib.dump(self.similarities_matrix, "BookClub/recommender_module/recommenders/resources/item_based_model/similarities_matrix.sav")

    """Import the trainset and the similarities_matrix from .sav files, using the joblib library."""
    def import_model(self):
        self.trainset = joblib.load("BookClub/recommender_module/recommenders/resources/item_based_model/trainset.sav")
        self.similarities_matrix = joblib.load("BookClub/recommender_module/recommenders/resources/item_based_model/similarities_matrix.sav")

    """Get the recommended books (up to 10) given a specified user_id, from all of the user's rated books"""
    def get_recommendations_all_ratings_from_user_id(self, user_id):
        user_ratings = self.get_trainset_user_book_ratings(user_id)
        recommendations = self.get_recommendations_from_user_inner_ratings(user_ratings)
        return recommendations

    """Get the recommended books (up to 10) given a specified user_id, from all of the user's positively (> 6/10) rated books"""
    def get_recommendations_positive_ratings_only_from_user_id(self, user_id, min_rating=6):
        user_ratings = self.get_trainset_user_book_ratings(user_id)
        positive_user_ratings = self.get_trainset_user_book_ratings(user_id, min_rating=min_rating)
        recommendations = self.get_recommendations_from_user_inner_ratings(positive_user_ratings, all_books_rated=user_ratings)
        return recommendations

    """Get all the ratings from the specified user, of books that are in the trainset, with a minimum rating value of {min_rating}"""
    def get_trainset_user_book_ratings(self, user_id, min_rating=0):
        items = self.data_provider.get_all_books_rated_by_user(user_id)
        inner_items = []
        for item in items:
            try:
                inner_item = self.trainset.to_inner_iid(item)
                rating = self.data_provider.get_rating_from_user_and_book(user_id, item)
                if (rating >= min_rating):
                    inner_items.append((inner_item, rating))
            except:
                pass
        return inner_items

    """Get recommendations from trainset, corresponding similarities matrix and user's ratings
        as inner ratings (from similarities matrix)"""
    def get_recommendations_from_user_inner_ratings(self, ratings, all_books_rated=None):

        # Define all books rated (read) by the user
        if all_books_rated == None:
            all_books_rated = ratings

        # Weigh items by rating
        candidates = defaultdict(float)
        for item_id, rating in ratings:
            similarity_row = self.similarities_matrix[item_id]
            for inner_id, score in enumerate(similarity_row):
                candidates[inner_id] += score * (rating / 5.0)

        # Get top-rated items from similar users
        library = Library()
        final_recommendations = []
        for item_id, rating_sum in sorted(candidates.items(), key=itemgetter(1), reverse=True):
            # Check if user has already read the book, and only recommend the book if it has some similarity
            if (not item_id in all_books_rated) and (not math.isnan(rating_sum)) and rating_sum != 0:
                try:
                    book_isbn = self.trainset.to_raw_iid(item_id)
                    book_title = library.get_book_title(book_isbn)
                    print(book_title, rating_sum)
                    final_recommendations.append(book_isbn)
                    if (len(final_recommendations) >= 10): # Get the top 10 recommendations
                        break
                except:
                    pass

        return final_recommendations
