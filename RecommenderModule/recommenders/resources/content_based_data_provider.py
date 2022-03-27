import pandas as pd
from BookClub.models import Book

"""This class loads the book depository dataset from the 'book_depository_dataset.csv' file,
    filters the dataset to keep only books from our database and compute a list of content for each book"""
class ContentBasedDataProvider:

    path_to_book_depository_dataset = "static/dataset/filtered_book_depository_dataset.csv"
    path_to_books_df = "static/dataset/BX_Books.csv"
    filtered_book_depository_dataset = None
    book_content_list = []

    def __init__(self, original_trainset=None, get_data_from_csv=False, print_status=False):
        if print_status:
            print("Getting data...")
        self.compute_filtered_book_depository_dataset(original_trainset, get_data_from_csv)
        self.make_list_of_dict_book_content()
        if print_status:
           print("Getting data done")

    """Import and return the book depository dataset from the 'book_depository_dataset.csv' file"""
    def get_book_depository_dataset(self):
        return pd.read_csv(self.path_to_book_depository_dataset)

    """Filter the book depository dataset to only keep rows containing books from our dataset"""
    def compute_filtered_book_depository_dataset(self, original_trainset, get_data_from_csv):
        book_depository_dataset = self.get_book_depository_dataset()
        if original_trainset is None:
            if get_data_from_csv:
                all_books = self.get_all_books_in_csv_dataset()
            else:
                all_books = self.get_all_books_in_django_database()
        else:
            all_books = self.get_all_books_in_trainset(original_trainset)
        self.filtered_book_depository_dataset = book_depository_dataset[book_depository_dataset["isbn10"].isin(all_books)]

    """Get all the books that are in the trainset to train the model from"""
    def get_all_books_in_trainset(self, original_trainset):
        all_books = [original_trainset.to_raw_iid(inner_item) for inner_item in original_trainset.all_items()]
        return all_books

    """Import the books dataset from the 'BX_Books.csv' file, and return a list of ISBNs for all books in the dataset"""
    def get_all_books_in_csv_dataset(self):
        books_df = pd.read_csv(self.path_to_books_df, sep=';', encoding_errors="ignore")
        all_books = list(books_df["ISBN"])
        return all_books

    """Get all books in the Django database, and return a list of ISBNs for all books in the dataset"""
    def get_all_books_in_django_database(self):
        books_query = Book.objects.all().values("ISBN")
        all_books = [book_object["ISBN"] for book_object in books_query]
        return all_books

    """Make a list containing a dictionary for each book in the filtered book depository dataset, 
        that contains: 'book_isbn', 'categories' (genres) and 'publication_year'"""
    def make_list_of_dict_book_content(self):
        filtered_book_depository_dataset = self.filtered_book_depository_dataset
        book_content_list = []
        for index, row in filtered_book_depository_dataset.iterrows():
            try:
                book_isbn = row["isbn10"]
                categories = row['categories'].strip('][').split(', ')
                publication_year = int(row["publication-date"][0:4])
                book_content_list.append({
                    "book_isbn": book_isbn,
                    "categories": categories,
                    "publication_year": publication_year
                })
            except:
                pass
        self.book_content_list = book_content_list

    """Return the list of book content dictionaries"""
    def get_list_of_dict_book_content(self):
        return self.book_content_list