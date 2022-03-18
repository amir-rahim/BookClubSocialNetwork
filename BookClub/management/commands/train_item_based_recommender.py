from django.core.management.base import BaseCommand
from RecommenderModule import user_recommendations_provider

class Command(BaseCommand):
        """Train and save item-based collaborative filtering model for item-based recommender."""

        def add_arguments(self, parser):
            parser.add_argument('min_ratings_threshold', type=int, nargs='?', default=15)
            parser.add_argument('min_support', type=int, nargs='?', default=5)

        def __init__(self):
            super().__init__()

        def handle(self, *args, **options):
            min_ratings_threshold = options.get('min_ratings_threshold', None)
            min_support = options.get('min_support', None)
            parameters = {}
            if min_ratings_threshold is not None:
                parameters["min_ratings_threshold"] = min_ratings_threshold
            if min_support is not None:
                parameters["min_support"] = min_support
            print("Started training item-based recommender...")
            user_recommendations_provider.retrain_item_based_recommender(parameters=parameters)
