from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
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
        file_path = "static/dataset/BX_Books_deployed.csv"

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
            
        print(str(len(random_sample)) + " books created")

    def cleanYear(self, year):
        string = str(year)
        if string == "0":
            return "0001-01-01"
        else:
            return string+"-01-01"
