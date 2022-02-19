import csv
import multiprocessing
from multiprocessing.pool import ThreadPool
from threading import Thread
import time
import requests
from queue import Queue
from bs4 import BeautifulSoup as BS
from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options

class DataRetriever():
    verbose = False
    def __init__(self, v=False, *args, **kwargs):
        self.verbose = v
  
    def getGenres(self, page):
        if(self.verbose):
            print("Getting genres:")
        soup = BS(page, 'lxml')
        listElements = soup.find_all("div", class_="elementList")
        genres = []
        for result in listElements:
            genre_element = result.find_all("a", class_="actionLinkLite bookPageGenreLink")
            outString = ""
            i = 0
            for element in genre_element:
                genres.append(element.text.strip())
                if(self.verbose):
                    i+=1
                    if i < len(genre_element):
                        outString += element.text.strip() + " -> "
                    else:
                        outString += element.text.strip()
            if(self.verbose):
                print(outString)  
        return genres
    
    def getISBN(self, request):
        pass
    
    def getTitle(self, request):
        soup = BS(request, "lxml")
        title = soup.find(id="bookTitle").text.strip()
        if(self.verbose):
            print(title)
        return title
        
    
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
        
class ISBNScraper():
    
    verbose = False
    
    def __init__(self, v=False, s=False, scrapeV=False, *args, **kwargs):
        self.verbose = v
        #if(s):
            #options = Options()
            #options.headless = True
            #self.requester = webdriver.Firefox(options=options)
        #else:
            #self.requester = requests
            
        self.retrieve = DataRetriever(v=scrapeV)
        
    def processBooks(self, isbns):
        pages = self.get_pagesM(isbns,8)
        books = self.scrape_books(isbns, pages)
        self.books_to_csv(books)
        
    def processPages(self, isbns):
        pages = self.get_pagesM(isbns, 8)
        self.page_to_csv(pages)
        
    def scrape_books(self, listOfISBNS, pages):
        
        books = []
    
        for page, isbn in pages:
            try:
                genres = self.retrieve.getGenres(page) 
                
                title = self.retrieve.getTitle(page)
                
                book = BookInfo(t=title, isbn=isbn, g=genres)
                books.append(book)
            except:
                continue
            
        return books
    
    def scrape_booksM(self, listOfISBNs, pages):
        
        pool = multiprocessing.Pool()
        pagesList = list(pages)
        results = pool.map(self.getBookInfoM, pagesList)
        pool.close()
        
        pool.join()
        
        return results
    
    def getBookInfoM(self, page):
        for page, isbn in page:
            try:
                genres = self.retrieve.getGenres(page) 
                
                title = self.retrieve.getTitle(page)
                
                book = BookInfo(t=title, isbn=isbn, g=genres)
                return book
            except:
                continue
            
            
    def get_pages(self, listOfISBNs):
        pages = []
        for isbn in listOfISBNs:
            url = "https://www.goodreads.com/search?q="+isbn
            self.requester.get(url)
            page = self.requester.page_source
            pages.append((page, isbn))
            
        return pages
    
    def get_pagesM(self, listOfISBNs, threads):
        pool = ThreadPool(processes=threads)
        result = pool.map(self.get_text, listOfISBNs)
        pool.close()
        pool.join()
        return result
    
    def newRequester(self, h=False, *args, **kwargs):
        options = Options()
        options.headless = True
        requester = webdriver.Firefox(options=options)
        return requester
            
    def books_to_csv(self, books):
        tic = time.time()
        with open(str(tic)+'.csv', 'w', newline='') as csvfile:
            write = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for book in books:
                name = book.title
                if self.verbose:
                    print(name)
                isbn = book.isbn
                subjects = book.genres
                write.writerow([name] + [isbn] + subjects)
            
        csvfile.close()
        
    def page_to_csv(self, pages):
        """
         Write pages to CSV. CSV Name will be the current time from time.time()

        Args:
            pages (List(String)): List of pages
        """
        tic = time.time()
        with open(str(tic)+'.csv', 'w', newline='') as csvfile:
            write = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for book in pages:
                write.writerow([book])
                
    def quit(self):
        self.requester.quit()

    def get_text(self, isbn):
        """
            Get the html of the goodreads page of the book represented by this ISBN.
            Returns a String pair (HTML, isbn)

        Args:
            isbn (String): Valid isbn of our book

        Returns:
            Pair(String, String): (HTMLText, isbn)
        """
        requester = self.newRequester()
        url = "https://www.goodreads.com/search?q="+isbn
        requester.get(url)
        page = requester.page_source
        requester.quit()
        return (page, isbn)
