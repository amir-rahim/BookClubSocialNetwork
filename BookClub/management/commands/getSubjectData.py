from django.core.management.base import BaseCommand
import time
from BookClub.models import Book
import pandas as pd
from pandas import DataFrame, MultiIndex
import requests
import multiprocessing
import csv

class Command(BaseCommand):
    """The database seeder."""
        
    def handle(self, *args, **options):
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
        books = books[:2000]
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