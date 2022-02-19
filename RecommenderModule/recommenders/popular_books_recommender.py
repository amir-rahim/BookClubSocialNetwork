from data_provider import DataProvider
import math
import numpy as np

"""This class allows the developer to recommend the most popular books to a user"""
class PopularBooks:
    
    data_provider = None
    filtered_books_list = []
    sorted_average_ratings = {}
    sorted_median_ratings = {}
    sorted_combination_scores = {}
    
    def __init__(self, min_ratings_threshold=100):
        self.load_filtered_books_list(min_ratings_threshold)
        self.compute_all_ratings()
        
    """Get all books with at least {self.min_ratings_threshold} user ratings"""
    def load_filtered_books_list(self, min_ratings_threshold):
        self.data_provider = DataProvider(filtering_min_ratings_threshold=min_ratings_threshold)
        self.filtered_books_list = self.data_provider.get_filtered_books_list()
        
    """Calculate popularity lists for all books according to the different metrics"""
    def compute_all_popularity_lists(self):
        self.compute_average_ratings()
        self.compute_median_ratings()
        self.compute_combination_ratings()
        
    """Get the average rating for the book with the given ISBN number"""
    def get_average_rating(self, isbn):
        ratings_arr = self.data_provider.get_all_ratings_for_isbn(isbn)
        sum = 0
        for rating in ratings_arr:
            sum += rating
        return sum / len(ratings_arr)
        
    """Calculate popularity list of all books according to the average of their ratings"""
    def compute_average_ratings(self):
        average_ratings = {}
        # Get average rating for all books
        for isbn in self.filtered_books_list:
            average_rating = self.get_average_rating(isbn)
            average_ratings[isbn] = average_rating
        # Sort books according to the average rating
        self.sorted_average_ratings = sorted(average_ratings.items(), key=lambda item: item[1], reverse=True)
        
    """Get the median rating for the book with the given ISBN number"""
    def get_median_rating(self, isbn):
        ratings_sorted_arr = np.sort(self.data_provider.get_all_ratings_for_isbn(isbn))
        if (len(ratings_sorted_arr) % 2 == 0): # even number of ratings
            index = len(ratings_sorted_arr) // 2
            median = (ratings_sorted_arr[index] + ratings_sorted_arr[index+1]) / 2
        else: # odd number of ratings
            index = (len(ratings_sorted_arr) // 2) + 1
            median = ratings_sorted_arr[index]
        return median
        
    """Calculate popularity list of all books according to the median of their ratings"""
    def compute_median_ratings(self):
        median_ratings = {}
        # Get median rating for all books
        for isbn in self.filtered_books_list:
            median_rating = self.get_median_rating(isbn)
            median_ratings[isbn] = median_rating
        # Sort books according to the median rating
        self.sorted_median_ratings = sorted(median_ratings.items(), key=lambda item: item[1], reverse=True)
        
    """Calculate popularity list of all books according to both the average and the median of their ratings"""
    def compute_combination_scores(self):
        combination_scores = {}
        # Get combinated score (from average and median) for all books
        for isbn in self.filtered_books_list:
            combination_score = math.sqrt(self.sorted_average_ratings[isbn] * self.sorted_median_ratings[isbn])
            combination_scores[isbn] = combination_score
        # Sort books according to the combinated score
        self.sorted_combination_scores = sorted(combination_scores.items(), key=lambda item: item[1], reverse=True)
        
    """Get most popular books (up to 10) from the given popularity list, that the user has not read yet"""
    def get_recommendations_from_popularity_list(self, popularity_list, user_read_books=[]):
        final_recommendations = []
        for (isbn, score) in popularity_list:
            if (not isbn in user_read_books) and (score > 0):
                final_recommendations.append(isbn)
                if (len(final_recommendations) >= 10):
                    break
        return final_recommendations
        
    """Get most popular books (up to 10) according to their average rating, that the user has not read yet"""
    def get_recommendations_from_average(self, user_read_books=[]):
        self.get_recommendations_from_popularity_list(self.sorted_average_ratings, user_read_books=user_read_books)
    
    """Get most popular books (up to 10) according to their median rating, that the user has not read yet"""
    def get_recommendations_from_median(self, user_read_books=[]):
        self.get_recommendations_from_popularity_list(self.sorted_median_ratings, user_read_books=user_read_books)
        
    """Get most popular books (up to 10) according to their average and median rating, that the user has not read yet"""
    def get_recommendations_from_average_and_median(self, user_read_books=[]):
        self.get_recommendations_from_popularity_list(self.sorted_combination_scores, user_read_books=user_read_books)