from multiprocessing.sharedctypes import Value
import os
from django.core.management.base import BaseCommand
import time
from BookClub.models import Book
import pandas as pd
from pandas import DataFrame
import requests
import multiprocessing
import csv
from surprise import Dataset
from surprise import Reader
from RecommenderModule.bookinfo import BookInfo

class Command(BaseCommand):
    """The database seeder."""
        
    def handle(self, *args, **options):
        tic = time.time()
        books = self.getSubjectsPool()
        unsuccessful = 0;
        with open('subjects.csv', 'w', newline='') as csvfile:
            for book in books:
                if book is not None:
                    write = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                    name = book.title
                    subjects = book.genres
                    isbn = book.isbn
                    if(subjects is not None):
                        write.writerow([name] + [isbn] + subjects)
                    else:
                        write.writerow([name] + [isbn])
                        unsuccessful += 1
                else:
                    unsuccessful += 1    
        toc = time.time()
        total = toc-tic
        items = len(books)
        itemTime = total/items
        print('Done in {:.4f} seconds'.format(total))
        print('Item time is :{:.4f} seconds'.format(itemTime))
        print("Number of successful books is " + str(items-unsuccessful))
        
    
    def getSubjectsPool(self):
        books = Book.objects.all()
        books = books
        pool = multiprocessing.Pool()
        print(os.cpu_count())
        result = pool.map(do_work, books)
        pool.close()
        
        pool.join()
        
        return result
    
    def bla(self):
        file_path = ("RecommenderModule/dataset/BX-Book-Ratings.csv")
        file = open(file_path,'rb',0)

        data = DataFrame(pd.read_csv(file_path,header=0,encoding = "ISO-8859-1",sep=';'))
        data = data.astype({"User-ID" : int, "ISBN" : str, "Book-Rating":int})
        reader = Reader(rating_scale=(0,10))

        dataset = Dataset.load_from_df(data, reader)

        counts = data.value_counts(subset = 'ISBN')

        book_file_path = ("RecommenderModule/dataset/BX_Books.csv")

        bookdata = DataFrame(pd.read_csv(book_file_path, header=0, encoding= "ISO-8859-1", sep=';'))


        countLimit = 5;
        # convert our series of isbn,counts into a list of tuples, then take only the first ten
        counts = list(counts.items())
        i = 0
        # for each isbn and count, print the count, then find the relevant row in the book csv and print it out
        for name, count in counts:
            if(count >= countLimit):
                i+=1
                #row = bookdata.loc[bookdata['ISBN'] == name, ['ISBN', 'Book-Title']]
                #if not(row.empty):
                #    print("Recommendations: " + str(count) + " for " + row['Book-Title'])
                #    print(" --- ")
                
        print(i)
        
def do_work(book):
    isbn = book.ISBN
    try:
        json = getJson(isbn)
        try:
            book = getBook(json, isbn)
            return book
        except TypeError:
            #print("No subject data for " + book.title)
            return None
    except ValueError:
        #print("No data returned at all for " + book.title)
        return None              
        
def getJson(isbn):
        url = "https://openlibrary.org/api/books?bibkeys=ISBN:"+isbn+"&jscmd=data&format=json"
        r = requests.get(url)
        if r.json() is None:
            raise ValueError
        return r.json()
    
def getBook(json, isbn):
    jsonKey = 'ISBN:' + isbn
    bookJson = json.get(jsonKey)
    if(bookJson is None):
        raise ValueError
    bookTitle = bookJson.get('title')
    bookSubjects = bookJson.get('subjects')
    return BookInfo(t=bookTitle, isbn=isbn, g=bookSubjects)

def getSubjectPairs(json, isbn):
    jsonKey = 'ISBN:' + isbn
    book = json.get(jsonKey)
    if(book is None):
        raise ValueError
    bookSubjects = (book.get('subjects'))
    if(bookSubjects is None):
        raise TypeError
    return(bookSubjects)