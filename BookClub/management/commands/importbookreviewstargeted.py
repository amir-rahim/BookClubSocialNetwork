
from django.core.management.base import BaseCommand
from faker import Faker
import faker
import pandas as pd
import time
from pandas import DataFrame
from BookClub.management.commands.helper import get_top_n_books, get_top_n_users_who_have_rated_xyz_books, get_top_n_books_shifted
from BookClub.models import User, BookReview, Book


class Command(BaseCommand):
    """The database seeder."""


    def handle(self, *args, **options):
        tic = time.time()
        model_instances = self.import_bookreviews()
        BookReview.objects.bulk_create(model_instances)
        toc = time.time()
        total = toc-tic
        print('Done in {:.4f} seconds'.format(total))
        print(str(len(model_instances)) + " reviews added")


    def import_bookreviews(self):
        file_path = ("static/dataset/BX-Book-Ratings.csv")

        data = DataFrame(pd.read_csv(file_path, header=0, encoding= "ISO-8859-1", sep=';'))
        book_isbns = get_top_n_books_shifted(300)
        user_ids = get_top_n_users_who_have_rated_xyz_books(1000, book_isbns)
        books = Book.objects.all().only('ISBN')
        users = User.objects.all().only('id')
        rows = data[data['ISBN'].isin(
            book_isbns) & data['User-ID'].isin(user_ids)]
        records = rows.to_dict('records')
        model_instances = self.process_records(records, books, users)
        return model_instances

            
        
    def process_records(self, records, books, users):
        reviews = []
        self.faker = Faker()
        book_error = 0
        for record in records:
            username = self.faker.unique.user_name()
            email = self.faker.unique.email()
            try:
                user = User.objects.get_or_create(id=record['User-ID'], defaults={'username': username, 'email': email, 'password':'pbkdf2_sha256$260000$qw2y9qdBlYmFUZVdkUqlOO$nuzhHvRnVDDOAo70OL14IEqk+bASVNTLjWS1N+c40VU='})[0]
                b = BookReview(
                    book=books.get(ISBN=record['ISBN']),
                    creator=user,
                    book_rating=record['Book-Rating'],
                    content=self.faker.paragraph(nb_sentences=3)
                )
                reviews.append(b)
            except Exception as e:
                book_error += 1
                continue

        print(book_error)
                

        return reviews