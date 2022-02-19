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

class Command(BaseCommand):
    """The database seeder."""
        
    def handle(self, *args, **options):
        self.bla()
        tic = time.time()
        pairs = self.getSubjectsPool()
        aDict = {}
        unsuccessful = 0;
        with open('subjects.csv', 'w', newline='') as csvfile:
            for pair in pairs:
                write = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                if pair is not None:
                    name = pair[0]
                    url = pair[1]
                    write.writerow([name])
                    if aDict.get(name) is None:
                        aDict[name] = url
                else:
                    unsuccessful += 1
                    
        toc = time.time()
        print('Done in {:.4f} seconds'.format(toc-tic))
        print("Unique subjects is " + str(len(aDict)))
        print("Number of successful books is " + str(len(pairs)-unsuccessful))
        
    def getSubjectsProcess(self):
        
        subjectsDict = {}
        self.noSubjects = []
        self.noInfo = []
        books = Book.objects.all()
        books = books[:5]
        i = 0
        processes = []
        for book in books:
            p = multiprocessing.Process(target=do_work, kwargs={'book':book})
            processes.append(p)
            p.start()
            i += 1
            if(i % 100 == 0):
                print(i)
                
        for process in processes:
            process.join()
            
        return subjectsDict
    
    def getSubjectsPool(self):
        books = Book.objects.all()
        books = books[:100]
        pool = multiprocessing.Pool()
        result = pool.map(do_work, books)
        pool.close()
        
        pool.join()
        
        return result
    
    def getSubjectsLinear(self):
        books = Book.objects.all()
        books = books[:100]
        result = map(do_work, books)
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
            subjectPairs = getSubjectPairs(json, isbn)
            for pair in subjectPairs:
                subjectName = pair['name']
                subjectURL = pair['url']
                return(subjectName,  subjectURL)
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

def getSubjectPairs(json, isbn):
        
    jsonKey = 'ISBN:' + isbn
    book = json.get(jsonKey)
    if(book is None):
        raise ValueError
    bookSubjects = (book.get('subjects'))
    if(bookSubjects is None):
        raise TypeError
    return(bookSubjects)