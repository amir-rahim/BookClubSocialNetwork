
from django.core.management.base import BaseCommand
import pandas as pd
import time
from pandas import DataFrame
from BookClub.models import User, BookReview, Book


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
        i = 0
        model_instances = []
        for book in books:
            rows = data.loc[(data['ISBN'] == book.ISBN)]
            records = rows.to_dict(orient="records")
            model_instances.extend(self.process_records(records, book, users))
        return model_instances
            
        
    def process_records(self, records, book, users):
        reviews = []
        for record in records:
            try:
                b = BookReview(
                    book=book,
                    creator=users.get(id=record['User-ID']),
                    book_rating=record['Book-Rating']
                )
                reviews.append(b)
            except Exception as e:
                continue

        return reviews