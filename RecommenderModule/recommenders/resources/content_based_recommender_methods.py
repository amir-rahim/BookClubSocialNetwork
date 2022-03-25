from RecommenderModule.recommenders.resources.library import Library
from RecommenderModule.recommenders.resources.content_based_data_provider import ContentBasedDataProvider
from collections import defaultdict
from operator import itemgetter
import joblib
import math

"""This class provides the developer with methods to recommend books to a user, 
    based on content similarity between books"""
class ContentBasedRecommenderMethods:

    path_to_model = "RecommenderModule/recommenders/resources/content_based_model"
    library = None
    content_based_data_provider = None
    book_content_list = []
    similarities_dictionary = {}

    def __init__(self, retraining=False, retraining_and_saving=False, trainset=None, get_data_from_csv=False):
        self.library = Library(trainset=trainset)
        if retraining or retraining_and_saving:
            self.build_book_content_list(trainset, get_data_from_csv)
            self.train_model()
            if retraining_and_saving:
                self.save_model()
        else:
            try:
                self.import_model()
            except:
                self.__init__(retraining_and_saving=True, trainset=trainset, get_data_from_csv=get_data_from_csv)


    """Build the list containing a dictionary for each book in the filtered book depository dataset, 
        which contains: 'book_isbn', 'categories' (genres) and 'publication_year' """
    def build_book_content_list(self, trainset, get_data_from_csv):
        content_based_data_provider = ContentBasedDataProvider(original_trainset=trainset, get_data_from_csv=get_data_from_csv)
        self.book_content_list = content_based_data_provider.get_list_of_dict_book_content()

    """Train the model on the defined data and build the associated similarities dictionary"""
    def train_model(self):
        similarities_dictionary = {}
        for book_content_dict_1 in self.book_content_list:
            book_isbn_1 = book_content_dict_1["book_isbn"]
            for book_content_dict_2 in self.book_content_list:
                book_isbn_2 = book_content_dict_2["book_isbn"]
                if not book_isbn_1 == book_isbn_2:
                    similarity = self.get_content_similarity_between_books(book_content_dict_1, book_content_dict_2)
                    if book_isbn_1 not in similarities_dictionary.keys():
                        similarities_dictionary[book_isbn_1] = {}
                    (similarities_dictionary[book_isbn_1])[book_isbn_2] = similarity
                    if book_isbn_2 not in similarities_dictionary.keys():
                        similarities_dictionary[book_isbn_2] = {}
                    (similarities_dictionary[book_isbn_2])[book_isbn_1] = similarity
        self.similarities_dictionary = similarities_dictionary

    """Get the overall similarity value (between 0 and 1) between the contents of 2 books"""
    def get_content_similarity_between_books(self, book_content_dict_1, book_content_dict_2):
        categories_similarity = self.compute_categories_similarity(book_content_dict_1["categories"], book_content_dict_2["categories"])
        publication_year_similarity = self.compute_publication_year_similarity(book_content_dict_1["publication_year"], book_content_dict_2["publication_year"])
        similarity = categories_similarity * publication_year_similarity
        return similarity

    """Calculate the similarity value (between 0 and 1) between the categories of 2 books"""
    def compute_categories_similarity(self, categories1, categories2):
        common_categories = [category for category in categories1 if category in categories2]
        if len(common_categories) == 0:
            return 0
        similarity = len(common_categories) / math.sqrt(len(categories1) * len(categories2))
        return similarity

    """Calculate the similarity value (between 0 and 1) between the publication years of 2 books"""
    def compute_publication_year_similarity(self, publication_year_1, publication_year_2):
        diff = abs(publication_year_1 - publication_year_2)
        similarity = math.exp(-diff / 10.0)
        return similarity

    """Save the similarities_dictionary as .sav file, using the joblib library."""
    def save_model(self):
        joblib.dump(self.similarities_dictionary, f"{self.path_to_model}/similarities_dictionary.sav")

    """Import the similarities_dictionary from the .sav file, using the joblib library."""
    def import_model(self):
        self.similarities_dictionary = joblib.load(f"{self.path_to_model}/similarities_dictionary.sav")


    """Get the recommended books (up to 10) given a specified user_id, from all of the user's positively (> 6/10) rated books"""
    def get_recommendations_positive_ratings_only_from_user_id(self, user_id, min_rating=6):
        all_ratings = self.library.get_all_ratings_by_user(user_id)
        positive_ratings = self.get_positive_ratings_from_all_ratings(all_ratings, min_rating=min_rating)
        recommendations = self.get_recommendations_from_positive_ratings(positive_ratings, all_ratings)
        return recommendations

    """Extract the inner ids of the ratings passed in the all_ratings argument,for books with a minimum rating value of {min_rating}"""
    def get_positive_ratings_from_all_ratings(self, all_ratings, min_rating=6):
        positive_ratings = []
        for book_isbn, rating in all_ratings:
            try:
                if rating >= min_rating:
                    positive_ratings.append((book_isbn, rating))
            except:
                pass
        return positive_ratings

    """Get the recommended books (up to 10) given a list of books rated positively and a list of all books rated
        by the user/club"""
    def get_recommendations_from_positive_ratings(self, positive_ratings, all_books_rated):

        # Weigh items by rating
        candidates = defaultdict(float)
        for item_id, rating in positive_ratings:
            try:
                similarity_row = self.similarities_dictionary[item_id]
                for book_isbn, similarity in similarity_row.items():
                    candidates[book_isbn] += similarity * (rating / 10.0)
            except:
                pass

        # Get top-rated items from similar users
        final_recommendations = []
        all_books_rated_isbn = [rating[0] for rating in all_books_rated]
        for book_isbn, rating_sum in sorted(candidates.items(), key=itemgetter(1), reverse=True):
            # Check if user has already read the book, and only recommend the book if it has some similarity
            if (book_isbn not in all_books_rated_isbn) and (not math.isnan(rating_sum)) and rating_sum != 0:
                try:
                    final_recommendations.append(book_isbn)
                    if len(final_recommendations) >= 10: # Get the top 10 recommendations
                        break
                except:
                    pass

        return final_recommendations

    """Get the recommended books (up to 10) given a specified club_url_name, from all of the club's members' positively (> 6/10) rated books"""
    def get_recommendations_positive_ratings_only_from_club_url_name(self, club_url_name, min_rating=6):
        all_ratings = self.library.get_all_ratings_by_club(club_url_name)
        positive_ratings = self.get_positive_ratings_from_all_ratings(all_ratings, min_rating=min_rating)
        recommendations = self.get_recommendations_from_positive_ratings(positive_ratings, all_ratings)
        return recommendations
