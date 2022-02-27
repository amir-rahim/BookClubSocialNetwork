import time
from BookClub.models import Book
import requests
import multiprocessing
import csv
from RecommenderModule.bookinfo import BookInfo



class Requester():
    
    def call(self):
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
        books = books[:100]
        pool = multiprocessing.Pool()
        result = pool.map(self.do_work, books)
        pool.close()
        
        pool.join()
        
        return result

    def do_work(self, book):
        isbn = book.ISBN
        try:
            json = self.getJson(isbn)
            try:
                book = self.getBook(json, isbn)
                return book
            except TypeError:
                #print("No subject data for " + book.title)
                return None
        except ValueError:
            #print("No data returned at all for " + book.title)
            return None              
            
    def getJson(self, isbn):
            url = "https://openlibrary.org/api/books?bibkeys=ISBN:"+isbn+"&jscmd=data&format=json"
            r = requests.get(url)
            if r.json() is None:
                raise ValueError
            return r.json()
        
    def getBook(self, json, isbn):
        jsonKey = 'ISBN:' + isbn
        bookJson = json.get(jsonKey)
        if(bookJson is None):
            raise ValueError
        bookTitle = bookJson.get('title')
        bookSubjects = bookJson.get('subjects')
        return BookInfo(t=bookTitle, isbn=isbn, g=bookSubjects)
