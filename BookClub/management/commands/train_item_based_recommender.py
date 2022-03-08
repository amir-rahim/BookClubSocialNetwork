from django.core.management.base import BaseCommand
from RecommenderModule import recommendations_provider

class Command(BaseCommand):
        """Train and save item-based collaborative filtering model for item-based recommender."""

        def add_arguments(self, parser):
            parser.add_argument('min_ratings_threshold', type=int, nargs='?', default=5)
            parser.add_argument('min_support', type=int, nargs='?', default=3)

        def __init__(self):
            super().__init__()

        def handle(self, *args, **options):
            min_ratings_threshold = options.get('min_ratings_threshold', None)
            min_support = options.get('min_support', None)
            print("Started training item-based recommender...")
            recommendations_provider.retrain_item_based_recommender(min_ratings_threshold=min_ratings_threshold, min_support=min_support)
