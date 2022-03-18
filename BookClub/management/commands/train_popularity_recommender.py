from django.core.management.base import BaseCommand
from RecommenderModule import user_recommendations_provider

class Command(BaseCommand):
        """Train and save popularity lists for popularity recommender."""

        def add_arguments(self, parser):
            parser.add_argument('min_ratings_threshold', type=int, nargs='?', default=5)

        def __init__(self):
            super().__init__()

        def handle(self, *args, **options):
            min_ratings_threshold = options.get('min_ratings_threshold', None)
            print("Started training popularity recommender...")
            user_recommendations_provider.retrain_popularity_recommender(min_ratings_threshold=min_ratings_threshold)
