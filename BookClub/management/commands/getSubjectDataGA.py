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
import json as JSON
from RecommenderModule.bookinfo import BookInfo

class Command(BaseCommand):
    """The database seeder."""
        
    def handle(self, *args, **options):
        #self.bla()
        tic = time.time()
        pairs = self.getSubjects()
        aDict = {}
        unsuccessful = 0;
        print(pairs)
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
    
    def getSubjects(self):
        books = Book.objects.all()
        books = books[:1]
        pool = multiprocessing.Pool()
        result = pool.map(do_work, books)
        pool.close()
        
        pool.join()
        
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
    url = "https://www.googleapis.com/books/v1/volumes?q=isbn:"+isbn+"&key="
    r = requests.get(url)
    if r.json() is None:
        raise ValueError
    return r.json()

def getSubjectPairs(json, isbn):
    book = json['items'][0]
    if(book is None):
        raise ValueError
    bookSubjects = (book.get('categories'))
    print(bookSubjects)
    if(bookSubjects is None):
        raise TypeError
    return(isbn, bookSubjects)