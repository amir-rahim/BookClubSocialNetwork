from django.core.management.base import BaseCommand
import random

from faker import Faker
from numpy import append
from BookClub.models import Book
import pandas as pd
from pandas import DataFrame
import os
import requests
from BookClub.models import user
from BookClub.models.review import BookReview

from BookClub.models.user import User


class Command(BaseCommand):
    """The database seeder."""

    def add_arguments(self, parser):
        parser.add_argument('books', type=int, nargs='?', default=5)

    def handle(self, *args, **options):
        file_path = "static/dataset/BX_Books.csv"

        # As we're loading a custom dataset, we need to define a reader. In the
        # movielens-100k dataset, each line has the following format:
        # 'user item rating timestamp', separated by '\t' characters.
        file = open(file_path, 'rb', 0)

        data = DataFrame(pd.read_csv(file_path, header=0, encoding="ISO-8859-1", sep=';'))

        df_records = data.to_dict('records')
        percent = options.get('books', None)

        model_instances = [Book(
            title=record['Book-Title'],
            ISBN=record['ISBN'],
            author=record['Book-Author'],
            publicationYear=self.cleanYear(record['Year-Of-Publication']),
            publisher=record['Publisher'],
            imageS=record['Image-URL-S'],
            imageM=record['Image-URL-M'],
            imageL=record['Image-URL-L'],
        ) for record in df_records]
        count = int(len(model_instances) * (percent / 100))
        random_sample = random.sample(model_instances, count)
        try:
            Book.objects.bulk_create(random_sample)
        except:
            print('unique error')
            
        self.importUsers()
        print(User.objects.all().count())
        self.importReviews()
        
    def cleanYear(self, year):
        string = str(year)
        if string == "0":
            return "0001-01-01"
        else:
            return string+"-01-01"
        
    def importUsers(self):
        file_path = ("RecommenderModule/dataset/BX-Users.csv")
        file = open(file_path, 'rb', 0)
        
        data = DataFrame(pd.read_csv(file_path, header=0, encoding= "ISO-8859-1", sep=';'))
        
        faker = Faker()
        
        df_records = data.to_dict('records')
        
        model_instances = []
        i = 0;
        for record in df_records:
            i +=1
            Faker.seed(i)
            u = User(
                username=faker.unique.user_name(),
                email=faker.unique.email(),
                password="Password123",
            )
            model_instances.append(u)
            
        
        try:
            User.objects.bulk_create(model_instances)
        except Exception as e:
            print(e)
            print("user error")
            print('unique error')
        
    def importReviews(self):
        file_path = ("RecommenderModule/dataset/BX-Book-Ratings.csv")
        file = open(file_path, 'rb', 0)
        
        data = DataFrame(pd.read_csv(file_path, header=0, encoding= "ISO-8859-1", sep=';'))
        
        df_records = data.to_dict('records')
        u = 0
        bc = 0
        i = 0
        model_instances = [ ]
        for record in df_records:
            try:
                i+=1
                if i % 10000 == 0:
                    print(i)
                if Book.objects.filter(ISBN=record['ISBN']).count() == 0:
                    bc += 1
                elif User.objects.filter(pk = record['User-ID']).count() == 0:
                    u += 1
                else:
                    b = BookReview(
                        book=self.getBook(record['ISBN']),
                        user=self.getUser(record['User-ID']),
                        rating=record['Book-Rating']
                    )
                    model_instances.append(b)
            except Exception as e:
                print(e)
                continue
            
        BookReview.objects.bulk_create(model_instances)
        
        print(u)
        print(bc)
        
        
    def getBook(self, isbn):
        return Book.objects.get(ISBN = isbn)
    
    def getUser(self, userId):
        return User.objects.get(pk=userId)
