from data_provider import DataProvider
from library import Library
from surprise import KNNBasic
from collections import defaultdict
from operator import itemgetter
import heapq
import math

"""This class allows the developer to recommend books to a user, similar to the user's rated books"""
class ItemBasedCollaborativeFiltering:

    data_provider = None
    trainset = None
    similarities_matrix = None

    def __init__(self, filtering_min_ratings_threshold=15):
        self.build_trainset(filtering_min_ratings_threshold)
        self.train_model()
    
    
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
    
    """Get the recommended books (up to 10) from a specified user_id"""
    def get_recommendations_from_user_id(self, user_id):
        user_ratings = self.get_trainset_user_book_ratings(user_id)
        recommendations = self.get_recommendations_from_user_inner_ratings(user_ratings)
        return recommendations
    
    """Get all the ratings from the specified user, of books that are in the trainset"""
    def get_trainset_user_book_ratings(self, user_id):
        items = self.data_provider.get_all_books_rated_by_user(user_id)
        inner_items = []
        for item in items:
            try:
                inner_item = self.trainset.to_inner_iid(item)
                rating = self.data_provider.get_rating_from_user_and_book(user_id, item)
                inner_items.append((inner_item, rating))
            except:
                pass
        return inner_items
    
    """Get recommendations from trainset, corresponding similarities matrix and user's ratings
        as inner ratings (from similarities matrix)"""
    def get_recommendations_from_user_inner_ratings(self, ratings):
        
        # Weigh items by rating
        candidates = defaultdict(float)
        for item_id, rating in ratings:
            similarity_row = self.similarities_matrix[item_id]
            for inner_id, score in enumerate(similarity_row):
                candidates[inner_id] += score * (rating / 5.0)
            
        # Get top-rated items from similar users
        library = Library()
        final_recommendations = []
        pos = 1
        for item_id, rating_sum in sorted(candidates.items(), key=itemgetter(1), reverse=True):
            # Check if user has already read the book, and only recommend the book if it has some similarity
            if (not item_id in ratings) and (not math.isnan(rating_sum)) and rating_sum != 0:
                try:
                    book_isbn = self.trainset.to_raw_iid(item_id)
                    book_title = library.get_book_title(book_isbn)
                    print(book_title, rating_sum)
                    final_recommendations.append(book_isbn)
                    pos += 1
                    if (pos > 10): # Get the top 10 recommendations
                        break
                except:
                    pass
                
        return final_recommendations
    
    
    
    """Get recommendations from trainset, corresponding similarities matrix and user's inner id
        (user must be part of trainset)"""
    def get_recommendations_from_inner_user(self, user_inner_id):
        
        # Get the top K items we rated
        user_ratings = self.trainset.ur[user_inner_id]
        k_neighbors = heapq.nlargest(10, user_ratings, key=lambda t: t[1])
        
        # Weigh items by rating
        candidates = defaultdict(float)
        for item_id, rating in k_neighbors:
            similarity_row = self.similarities_matrix[item_id]
            for inner_id, score in enumerate(similarity_row):
                candidates[inner_id] += score * (rating / 5.0)
            
        # Build a dictionary of stuff the user has already seen
        watched = {}
        for item_id, rating in self.trainset.ur[user_inner_id]:
            watched[item_id] = 1
            
        # Get top-rated items from similar users
        library = Library()
        final_recommendations = []
        pos = 0
        for item_id, rating_sum in sorted(candidates.items(), key=itemgetter(1), reverse=True):
            if not item_id in watched:
                try:
                    book_isbn = self.trainset.to_raw_iid(item_id)
                    book_title = library.get_book_title(book_isbn)
                    print(book_title, rating_sum)
                    final_recommendations.append(book_isbn)
                    pos += 1
                    if (pos > 10):
                        break
                except:
                    pass
                
        return final_recommendations