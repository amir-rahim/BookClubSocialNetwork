from surprise import Dataset
from surprise import Reader
import pandas as pd
from BookClub.models.review import BookReview


"""This class loads the ratings dataset from the 'BX-Book-Ratings.csv' file and builds the train sets"""
class DataProvider:

    ratings_path = "static/dataset/BX-Book-Ratings.csv"
    ratings_trainset = None
    ratings_df = None
    train_df = None
    test_df = None
    filtering_min_ratings_threshold = 1
    filtered_ratings_df = None
    filtered_ratings_dataset = None
    filtered_ratings_trainset = None

    """Constructor for the DataProvider class
        train_dataset_size_percentage (value between 0 and 1): (unfiltered dataset) percentage of dataset to use in training dataset (rest used in testing dataset)
        filtering_min_ratings_threshold: minimum number of ratings for books to be included in the filtered ratings dataset"""
    def __init__(self, train_dataset_size_percentage=0.01, filtering_min_ratings_threshold=15, get_data_from_csv=False, print_status=False):
        if print_status:
            print("Getting data...")
        self.train_dataset_size_percentage = train_dataset_size_percentage
        self.load_ratings_datasets(get_data_from_csv)
        self.filtering_min_ratings_threshold = filtering_min_ratings_threshold
        self.load_filtered_ratings_dataset()
        if print_status:
           print("Getting data done")

    """Load the ratings from the csv file, split the data in train and test partitions, and build train set"""
    def load_ratings_datasets(self, get_data_from_csv=False):
        if get_data_from_csv:
            # Get data from csv as pandas DataFrame
            ratings_df = pd.read_csv(self.ratings_path, sep=';', encoding_errors="ignore")
            self.ratings_df = ratings_df
        else:
            self.get_ratings_from_django_database()

    """Get data from Django database as pandas DataFrame"""
    def get_ratings_from_django_database(self):
        ratings_query = BookReview.objects.all()
        ratings_list = []
        for rating in ratings_query:
            ratings_list.append([rating.user.username, rating.book.ISBN, rating.book_rating])
        ratings_df = pd.DataFrame.from_records(ratings_list, columns=["User-ID", "ISBN", "Book-Rating"])
        self.ratings_df = ratings_df

    """Filter the book dataset to keep only books with at least {self.filtering_min_ratings_threshold} ratings"""
    def get_filtered_books_list(self):
        # Get original data from csv
        ratings_df = self.ratings_df
        ratings_counts = ratings_df["ISBN"].value_counts()
        # Get list of all books with at least {self.filtering_min_ratings_threshold} ratings
        filtered_books_list = []
        for isbn, count in ratings_counts.items():
          if count >= self.filtering_min_ratings_threshold:
            filtered_books_list.append(isbn)
        return filtered_books_list

    """Filter the original dataset to keep only books having at least
        {self.filtering_min_ratings_threshold} (defined in constructor) ratings
        (100% of dataset goes into training)"""
    def load_filtered_ratings_dataset(self):
        # Get original data from csv
        ratings_df = self.ratings_df
        # Get list of all books with at least {self.filtering_min_ratings_threshold} ratings
        filtered_books_list = self.get_filtered_books_list()
        # Filter the original DataFrame to only keep the books having at least {self.filtering_min_ratings_threshold} ratings
        filtered_ratings_df = ratings_df.loc[ratings_df["ISBN"].isin(filtered_books_list)]
        self.filtered_ratings_df = filtered_ratings_df
        # Create surprise dataset
        reader = Reader(line_format='user item rating', sep=';', skip_lines=0, rating_scale=(0,10))
        filtered_ratings_dataset = Dataset.load_from_df(filtered_ratings_df, reader)
        self.filtered_ratings_dataset = filtered_ratings_dataset
        self.filtered_ratings_trainset = filtered_ratings_dataset.build_full_trainset()

    """Get the filtered ratings dataset object"""
    def get_filtered_ratings_dataset(self):
        return self.filtered_ratings_dataset

    """Get the filtered ratings train set"""
    def get_filtered_ratings_trainset(self):
        return self.filtered_ratings_trainset
