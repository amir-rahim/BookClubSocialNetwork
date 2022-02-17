from django.core.management.base import BaseCommand
from faker import Faker
import random
from BookClub.models import Book
from django.db.utils import IntegrityError
import pandas as pd
from pandas import Series
from pandas import DataFrame

class Command(BaseCommand):
    """The database seeder."""
        
    def add_arguments(self, parser):
        parser.add_argument('books', type=int, nargs='?', default=5)
        
    def handle(self, *args, **options):
        file_path = ("RecommenderModule/dataset/BX_Books.csv")

        # As we're loading a custom dataset, we need to define a reader. In the
        # movielens-100k dataset, each line has the following format:
        # 'user item rating timestamp', separated by '\t' characters.
        file = open(file_path,'rb',0)

        data = DataFrame(pd.read_csv(file_path, header=0, encoding= "ISO-8859-1", sep=';'))
        
        df_records = data.to_dict('records')
        percent = options.get('books', None)
        
        model_instances = [Book(
            title = record['Book-Title'],
            ISBN = record['ISBN'],
            author = record['Book-Author'],
            publicationYear = self.cleanYear(record['Year-Of-Publication']),
            publisher = record['Publisher'],
            imageS = record['Image-URL-S'],
            imageM = record['Image-URL-M'], 
            imageL = record['Image-URL-L'],
        ) for record in df_records]
        count = int(len(model_instances)*(percent/100))
        random_sample = random.sample(model_instances, count)
        Book.objects.bulk_create(random_sample)
        
    def cleanYear(self, year):
        string = str(year)
        if string == "0":
            return "0001-01-01"
        else:
            return string+"-01-01"