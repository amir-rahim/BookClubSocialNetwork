from resources.item_based_collaborative_filtering_methods import ItemBasedCollaborativeFilteringMethods

"""This class allows the developer to recommend books to a user, similar to the user's rated books"""
class ItemBasedRecommender:
    
    item_based = None
    
    def __init__(self, filtering_min_ratings_threshold=15):
        self.item_based = ItemBasedCollaborativeFilteringMethods(filtering_min_ratings_threshold=filtering_min_ratings_threshold)
        
        
    """Get the recommended books (up to 10) given a specified user_id, from all of the user's rated books"""
    def get_recommendations_all_ratings_from_user_id(self, user_id):
        return self.item_based.get_recommendations_all_ratings_from_user_id(user_id)
    
    """Get the recommended books (up to 10) given a specified user_id, from all of the user's positively (> 6/10) rated books"""
    def get_recommendations_positive_ratings_only_from_user_id(self, user_id, min_rating=6):
        return self.item_based.get_recommendations_positive_ratings_only_from_user_id(user_id, min_rating=min_rating)