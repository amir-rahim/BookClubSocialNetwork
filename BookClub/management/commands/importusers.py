from django.core.management.base import BaseCommand
import random
from faker import Faker
import pandas as pd
from pandas import DataFrame
import time

from BookClub.models.user import User


class Command(BaseCommand):
    """The database seeder."""

    def add_arguments(self, parser):
        parser.add_argument('users', type=int, nargs='?', default=5)

    def handle(self, *args, **options):
        tic = time.time()
        percent = options.get('users', None)
        model_instances = self.import_users()
        count = int(len(model_instances) * (percent / 100))
        random_sample = random.sample(model_instances, count)
        try:
            User.objects.bulk_create(random_sample)
        except Exception as e:
            print(e)
        toc = time.time()
        total = toc-tic
        print('Done in {:.4f} seconds'.format(total))
        print(str(len(random_sample)) + " Users created")

    def import_users(self):
        file_path = ("static/dataset/BX-Users.csv")
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
                password='pbkdf2_sha256$260000$qw2y9qdBlYmFUZVdkUqlOO$nuzhHvRnVDDOAo70OL14IEqk+bASVNTLjWS1N+c40VU=',
            )
            model_instances.append(u)

        return model_instances
