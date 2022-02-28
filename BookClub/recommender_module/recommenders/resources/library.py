import pandas as pd

"""This class acts as a library to recover information about a book"""
class Library:
    
    books_path = "resources/book-review-dataset/BX_Books.csv"
    books_df = None
    
    def __init__(self):
        self.load_books_dataset()
        
    """Load the books into a pandas DataFrame, from the 'BX_Books.csv' file"""
    def load_books_dataset(self):
        # Get data from csv as pandas DataFrame
        books_df = pd.read_csv(self.books_path, sep=';', encoding_errors="ignore")
        self.books_df = books_df
    
    """Get the title of the book, given its ISBN value"""
    def get_book_title(self, book_isbn):
        book_title = ((self.books_df.loc[self.books_df["ISBN"] == book_isbn])["Book-Title"]).values[0]
        return book_title
            