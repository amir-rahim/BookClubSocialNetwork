from RecommenderModule.recommenders.resources.data_provider import DataProvider
from RecommenderModule.recommenders.resources.library import Library
import math
import numpy as np
import joblib

"""This class provides the developer with methods to recommend the most popular books to a user"""
class PopularBooksMethods:

    path_to_popularity_lists = "RecommenderModule/recommenders/resources/popularity_lists"
    data_provider = None
    trainset = None
    library = None
    filtered_books_list = []
    average_ratings = {}
    sorted_average_ratings = []
    median_ratings = {}
    sorted_median_ratings = []
    sorted_combination_scores = []

    def __init__(self, min_ratings_threshold=100, retraining=False, retraining_and_saving=False, trainset=None):
        if (trainset == None):
            if (retraining or retraining_and_saving):
                self.load_filtered_books_list(min_ratings_threshold)
                self.compute_all_popularity_lists()
                if (retraining_and_saving):
                    self.save_all_popularity_lists()
            else:
                # Import popularity lists if files exist, otherwise train and save popularity lists
                try:
                    self.import_trained_lists()
                except:
                    self.__init__(min_ratings_threshold=min_ratings_threshold, retraining_and_saving=True)
        else:
            self.trainset = trainset
            self.load_filtered_books_list(None)
            self.compute_all_popularity_lists()
        self.library = Library(trainset=self.trainset)


    """Import all sorted ratings list objects, using the joblib library"""
    def import_trained_lists(self):
        self.sorted_average_ratings = joblib.load(f"{self.path_to_popularity_lists}/sorted_average_ratings.sav")
        self.sorted_median_ratings = joblib.load(f"{self.path_to_popularity_lists}/sorted_median_ratings.sav")
        self.sorted_combination_scores = joblib.load(f"{self.path_to_popularity_lists}/sorted_combination_scores.sav")

    """Get all books with at least {self.min_ratings_threshold} user ratings"""
    def load_filtered_books_list(self, min_ratings_threshold):
        if (self.trainset == None):
            self.data_provider = DataProvider(filtering_min_ratings_threshold=min_ratings_threshold)
            self.filtered_books_list = self.data_provider.get_filtered_books_list()
            self.trainset = self.data_provider.filtered_ratings_trainset
        else:
            books_list = []
            for item_inner_id in self.trainset.all_items():
                books_list.append(self.trainset.to_raw_iid(item_inner_id))
            self.filtered_books_list = books_list

    """Calculate popularity lists for all books according to the different metrics"""
    def compute_all_popularity_lists(self):
        self.compute_sorted_average_ratings()
        self.compute_sorted_median_ratings()
        self.compute_sorted_combination_scores()

    """Save all computed popularity lists into .sav files, using the joblib library"""
    def save_all_popularity_lists(self):
        joblib.dump(self.sorted_average_ratings, f"{self.path_to_popularity_lists}/sorted_average_ratings.sav")
        joblib.dump(self.sorted_median_ratings, f"{self.path_to_popularity_lists}/sorted_median_ratings.sav")
        joblib.dump(self.sorted_combination_scores, f"{self.path_to_popularity_lists}/sorted_combination_scores.sav")

    """Get the average rating for the book with the given ISBN number"""
    def get_average_rating(self, isbn):
        ratings_arr = self.library.get_all_ratings_for_isbn(isbn)
        sum = 0
        for rating in ratings_arr:
            sum += rating
        return sum / len(ratings_arr)

    """Calculate popularity list of all books according to the average of their ratings"""
    def compute_sorted_average_ratings(self):
        print("Computing popularity list from average ratings...")
        average_ratings = {}
        # Get average rating for all books
        for isbn in self.filtered_books_list:
            average_rating = self.get_average_rating(isbn)
            average_ratings[isbn] = average_rating
        self.average_ratings = average_ratings
        # Sort books according to the average rating
        self.sorted_average_ratings = sorted(average_ratings.items(), key=lambda item: item[1], reverse=True)
        print("Done computing popularity list.")

    """Get the median rating for the book with the given ISBN number"""
    def get_median_rating(self, isbn):
        ratings_sorted_arr = np.sort(self.library.get_all_ratings_for_isbn(isbn))
        if (len(ratings_sorted_arr) % 2 == 0): # even number of ratings
            index = len(ratings_sorted_arr) // 2
            median = (ratings_sorted_arr[index] + ratings_sorted_arr[index+1]) / 2
        else: # odd number of ratings
            index = (len(ratings_sorted_arr) // 2) + 1
            median = ratings_sorted_arr[index]
        return median

    """Calculate popularity list of all books according to the median of their ratings"""
    def compute_sorted_median_ratings(self):
        print("Computing popularity list from median ratings...")
        median_ratings = {}
        # Get median rating for all books
        for isbn in self.filtered_books_list:
            median_rating = self.get_median_rating(isbn)
            median_ratings[isbn] = median_rating
        self.median_ratings = median_ratings
        # Sort books according to the median rating
        self.sorted_median_ratings = sorted(median_ratings.items(), key=lambda item: item[1], reverse=True)
        print("Done computing popularity list.")

    """Calculate popularity list of all books according to both the average and the median of their ratings"""
    def compute_sorted_combination_scores(self):
        print("Computing popularity list from average and median ratings...")
        combination_scores = {}
        # Get combinated score (from average and median) for all books
        for isbn in self.filtered_books_list:
            combination_score = math.sqrt(self.average_ratings[isbn] * self.median_ratings[isbn])
            combination_scores[isbn] = combination_score
        # Sort books according to the combinated score
        self.sorted_combination_scores = sorted(combination_scores.items(), key=lambda item: item[1], reverse=True)
        print("Done computing popularity list.")

    """Get most popular books (up to 10) from the given popularity list, that the user has not read yet"""
    def get_recommendations_from_popularity_list(self, popularity_list, user_read_books=[]):
        final_recommendations = []
        for (isbn, score) in popularity_list:
            if (isbn not in user_read_books) and (score > 0):
                #print(f"{isbn}: {score}")
                final_recommendations.append(isbn)
                if (len(final_recommendations) >= 10):
                    break
        return final_recommendations

    """Get most popular books (up to 10) according to their average rating, that the user has not read yet"""
    def get_recommendations_from_average(self, user_read_books=[]):
        return self.get_recommendations_from_popularity_list(self.sorted_average_ratings, user_read_books=user_read_books)

    """Get most popular books (up to 10) according to their median rating, that the user has not read yet"""
    def get_recommendations_from_median(self, user_read_books=[]):
        return self.get_recommendations_from_popularity_list(self.sorted_median_ratings, user_read_books=user_read_books)

    """Get most popular books (up to 10) according to their average and median rating, that the user has not read yet"""
    def get_recommendations_from_average_and_median(self, user_read_books=[]):
        return self.get_recommendations_from_popularity_list(self.sorted_combination_scores, user_read_books=user_read_books)
