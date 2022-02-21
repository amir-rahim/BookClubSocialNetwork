import csv
from multiprocessing.pool import ThreadPool
import time
from bs4 import BeautifulSoup as BS
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from .bookinfo import BookInfo

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
        BookInfo.books_to_csv(books)
        
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
import multiprocessing