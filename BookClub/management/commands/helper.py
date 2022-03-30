import pandas as pd
from pandas import DataFrame

def get_top_n_books(n):
    ratings_file_path = "static/dataset/BX-Book-Ratings.csv"
    rating_data = DataFrame(pd.read_csv(
        ratings_file_path, header=0, encoding="ISO-8859-1", sep=';'))

    ratings_counts = rating_data["ISBN"].value_counts()

    isbns = ratings_counts.head(n).index.to_list()
    return isbns


def get_top_n_books_shifted(n):
    ratings_file_path = "static/dataset/BX-Book-Ratings.csv"
    rating_data = DataFrame(pd.read_csv(
        ratings_file_path, header=0, encoding="ISO-8859-1", sep=';'))

    ratings_counts = rating_data["ISBN"].value_counts()

    isbns = ratings_counts.head(n+2700)
    isbns = isbns.tail(n).index
    return isbns

def get_top_n_users_who_have_rated_xyz_books(n, xyz):
    rating_data = DataFrame(pd.read_csv(
        "static/dataset/BX-Book-Ratings.csv", header=0, encoding="ISO-8859-1", sep=';'))
    ratings_for_chosen_books = rating_data[rating_data["ISBN"].isin(xyz)]
    rating_users = ratings_for_chosen_books["User-ID"].value_counts()
    rating_users = rating_users.head(1000).index.to_list()
    return rating_users