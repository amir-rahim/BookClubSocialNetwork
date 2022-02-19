import random
from django.core.management.base import BaseCommand
from BookClub.models import Book
from RecommenderModule.scraper import *


class Command(BaseCommand):
    """The database seeder."""
    
    def add_arguments(self, parser):
        parser.add_argument('books', type=int, nargs='?', default=5)
        
    def handle(self, *args, **options):
        tic = time.time()
        percent = options.get('books', None)
        books = Book.objects.all()
        count = int(len(books)*(percent/100))
        sample = random.sample(list(books),1) 
        def getISBN(book):
            return book.ISBN
        
        isbns = map(getISBN, sample)
        isbnList = list(isbns)
        scraper = ISBNScraper(s=True)
        scraper.processBooks(isbnList)           
        #scraper.quit()
        toc = time.time()
        print('Done in {:.4f} seconds'.format(toc-tic))
            
        
        

