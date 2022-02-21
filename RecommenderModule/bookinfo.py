import csv
import time

class BookInfo():
    
    def __init__(self, t="", isbn="", g=[], *args, **kwargs):
        self.genres = g
        self.title = t
        self.isbn = isbn
        
    def __str__(self):
        return self.title
    
    def genres(self):
        return self.genres
    
    def title(self):
        return self.title
    
    def isbn(self):
        return self.isbn
    
    def setGenres(self, genres):
        self.genres = genres
        
    def isbn(self, isbn):
        self.isbn = isbn
        
    def title(self, title):
        self.title = title
    
    @classmethod
    def books_to_csv(self, books):
        tic = time.time()
        with open(str(tic)+'.csv', 'w', newline='') as csvfile:
            write = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for book in books:
                name = book.title
                isbn = book.isbn
                subjects = book.genres
                write.writerow([name] + [isbn] + subjects)
            
        csvfile.close()
        