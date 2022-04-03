
from django.core.management.base import BaseCommand
import pandas as pd
import time
from pandas import DataFrame
from BookClub.models import User, BookReview, Book
from faker import Faker

class Command(BaseCommand):
    """The database seeder."""

    def add_arguments(self, parser):
        parser.add_argument('reviews', type=int, nargs='?', default=5)

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
        
        books = Book.objects.all().only('ISBN')
        users = User.objects.all().only('id')
        len(books)
        len(users)
        books = Book.objects.all().only('ISBN')
        users = User.objects.all().only('id')
        rows = data[data['ISBN'].isin(
            books.values_list('ISBN',flat=True))]
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
                user = User.objects.get_or_create(id=record['User-ID'], defaults={
                                                  'username': username, 'email': email, 'password': 'pbkdf2_sha256$260000$qw2y9qdBlYmFUZVdkUqlOO$nuzhHvRnVDDOAo70OL14IEqk+bASVNTLjWS1N+c40VU='})[0]
                b = BookReview(
                    book=books.get(ISBN=record['ISBN']),
                    creator=user,
                    book_rating=record['Book-Rating'],
                    title=self.faker.sentence(nb_words=3),
                    content=self.faker.paragraph(nb_sentences=3)
                )
                reviews.append(b)
                if len(reviews) % 100000 == 0:
                    print(str(len(reviews)) + " found so far")
            except Exception as e:
                book_error += 1
                continue

        print(book_error)
        
        return reviews
