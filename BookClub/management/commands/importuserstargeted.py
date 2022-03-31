from django.core.management.base import BaseCommand
import random
from faker import Faker
import pandas as pd
from pandas import DataFrame
import time
from BookClub.management.commands.helper import get_top_n_books, get_top_n_users_who_have_rated_xyz_books, get_top_n_books_shifted

from BookClub.models.user import User


class Command(BaseCommand):
    """The database seeder."""

    def handle(self, *args, **options):
        tic = time.time()
        model_instances = self.import_users()
        try:
            User.objects.bulk_create(model_instances)
        except Exception as e:
            print(e)
        toc = time.time()
        total = toc-tic
        print('Done in {:.4f} seconds'.format(total))
        print(str(len(model_instances)) + " Users created")

    def import_users(self):
        file_path = ("static/dataset/BX-Users.csv")

        data = DataFrame(pd.read_csv(file_path, header=0, encoding= "ISO-8859-1", sep=';'))

        isbns = get_top_n_books_shifted(300)
        rating_users = get_top_n_users_who_have_rated_xyz_books(1000, isbns)
        faker = Faker()

        chosen_users = data[data['User-ID'].isin(rating_users)]
        chosen_users = chosen_users.to_dict('records')

        model_instances = []
        i = 0;
        for record in chosen_users:
            i +=1
            Faker.seed(i)
            u = User(
                pk=i,
                username=faker.unique.user_name(),
                email=faker.unique.email(),
                password='pbkdf2_sha256$260000$qw2y9qdBlYmFUZVdkUqlOO$nuzhHvRnVDDOAo70OL14IEqk+bASVNTLjWS1N+c40VU=',
            )
            model_instances.append(u)

        return model_instances
