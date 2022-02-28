from resources.popular_books_recommender_methods import PopularBooksMethods

"""This class allows the developer to recommend the most popular books to a user"""
class PopularBooksRecommender:
    
    popular_books = None
    
    def __init__(self, min_ratings_threshold=100):
        self.popular_books = PopularBooksMethods(min_ratings_threshold=min_ratings_threshold)
        
    
    """Get most popular books (up to 10) according to their average rating, that the user has not read yet"""
    def get_recommendations_from_average(self, user_read_books=[]):
        return self.popular_books.get_recommendations_from_average(user_read_books=user_read_books)
    
    """Get most popular books (up to 10) according to their median rating, that the user has not read yet"""
    def get_recommendations_from_median(self, user_read_books=[]):
        return self.popular_books.get_recommendations_from_median(user_read_books=user_read_books)
        
    """Get most popular books (up to 10) according to their average and median rating, that the user has not read yet"""
    def get_recommendations_from_average_and_median(self, user_read_books=[]):
        return self.popular_books.get_recommendations_from_average_and_median(user_read_books=user_read_books)
