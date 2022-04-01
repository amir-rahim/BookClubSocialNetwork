from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
import random

from faker import Faker
from numpy import append
from BookClub.management.commands.helper import get_top_n_books, get_top_n_books_shifted
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

    def handle(self, *args, **options):
        file_path = "static/dataset/BX_Books.csv"
        
        

        book_data = DataFrame(pd.read_csv(file_path, header=0, encoding="ISO-8859-1", sep=';'))
        isbns = get_top_n_books_shifted(300)
        
        chosen_books = book_data[book_data['ISBN'].isin(isbns)]
        chosen_books_records = chosen_books.to_dict('records')
        model_instances = [Book(
            title=record['Book-Title'],
            ISBN=record['ISBN'],
            author=record['Book-Author'],
            publicationYear=self.cleanYear(record['Year-Of-Publication']),
            publisher=record['Publisher'],
            imageS=record['Image-URL-S'],
            imageM=record['Image-URL-M'],
            imageL=record['Image-URL-L'],
        ) for record in chosen_books_records]
        try:
            Book.objects.bulk_create(model_instances)
        except Exception as e:
            print(e)
            print("no books added")
            return
            
        print(str(len(model_instances)) + " books created")

    def cleanYear(self, year):
        string = str(year)
        if string == "0":
            return "0001-01-01"
        else:
            return string+"-01-01"
