from surprise import Dataset
from surprise import Reader
import pandas as pd

"""This class loads the ratings dataset from the 'BX-Book-Ratings.csv' file and builds the train sets"""
class DataProvider:

    ratings_path = "book-review-dataset/BX-Book-Ratings.csv"
    ratings_trainset = None
    ratings_df = None
    train_df = None
    test_df = None
    filtering_min_ratings_threshold = 1
    filtered_ratings_df = None
    filtered_ratings_trainset = None
    
    """Constructor for the DataProvider class
        train_dataset_size_percentage (value between 0 and 1): (unfiltered dataset) percentage of dataset to use in training dataset (rest used in testing dataset)
        filtering_min_ratings_threshold: minimum number of ratings for books to be included in the filtered ratings dataset"""
    def __init__(self, train_dataset_size_percentage=0.01, filtering_min_ratings_threshold=15):
        self.train_dataset_size_percentage = train_dataset_size_percentage
        self.load_ratings_datasets()
        self.filtering_min_ratings_threshold = filtering_min_ratings_threshold
        self.load_filtered_ratings_dataset()
        
    """Load the ratings from the csv file, split the data in train and test partitions, and build train set"""
    def load_ratings_datasets(self):
        # Get data from csv as pandas DataFrame
        ratings_df = pd.read_csv(self.ratings_path, sep=';', encoding_errors="ignore")
        self.ratings_df = ratings_df
        # Split data into train (70%) and test (30%) DataFrames
        index_split = int(len(ratings_df)*self.train_dataset_size_percentage)
        train_df = ratings_df.iloc[0:index_split, :]
        self.train_df = train_df
        test_df = ratings_df.iloc[index_split:, :]
        self.test_df = test_df
        # Create surprise dataset
        reader = Reader(line_format='user item rating', sep=';', skip_lines=0, rating_scale=(0,10))
        ratings_trainset = Dataset.load_from_df(train_df, reader)
        self.ratings_trainset = ratings_trainset.build_full_trainset()
        
        
    """Filter the original dataset to keep only books having at least
        {self.filtering_min_ratings_threshold} (defined in constructor) ratings 
        (100% of dataset goes into training)"""
    def load_filtered_ratings_dataset(self):
        # Get original data from csv
        ratings_df = self.ratings_df
        ratings_counts = ratings_df["ISBN"].value_counts()
        # Get list of all books with at least 10 ratings
        books_over_10_ratings = []
        for isbn in ratings_counts.keys():
          if ratings_counts[isbn] >= self.filtering_min_ratings_threshold:
            books_over_10_ratings.append(isbn)
        # Filter the original DataFrame to only keep the books having at least 10 ratings
        filtered_ratings_df = ratings_df.loc[ratings_df["ISBN"].isin(books_over_10_ratings)]
        self.filtered_ratings_df = filtered_ratings_df
        # Create surprise dataset
        reader = Reader(line_format='user item rating', sep=';', skip_lines=0, rating_scale=(0,10))
        filtered_ratings_trainset = Dataset.load_from_df(filtered_ratings_df, reader)
        self.filtered_ratings_trainset = filtered_ratings_trainset.build_full_trainset()

    """Get the non-filtered ratings train set"""
    def get_ratings_trainset(self):
        return self.ratings_trainset
    
    """Get the filtered ratings train set"""
    def get_filtered_ratings_trainset(self):
        return self.filtered_ratings_trainset
    
    """Get the ISBN value of all books the specified user has rated"""
    def get_all_books_rated_by_user(self, user_id):
        books = (self.ratings_df.loc[self.ratings_df["User-ID"] == user_id])["ISBN"].values
        return books
    
    """Get the rating the specified user made for the specified book"""
    def get_rating_from_user_and_book(self, user_id, book_isbn):
        user_ratings = self.ratings_df.loc[self.ratings_df["User-ID"] == user_id]
        rating = (user_ratings.loc[user_ratings["ISBN"] == book_isbn])["Book-Rating"].values[0]
        return rating