from django.core.management.base import BaseCommand
from RecommenderModule import recommendations_provider

class Command(BaseCommand):
        """Train and save content-based similarities dictionary for content-based recommender."""

        def __init__(self):
            super().__init__()

        def handle(self, *args, **options):
            print("Started training content-based recommender...")
            recommendations_provider.retrain_content_based_recommender()
            print("Done training content-based recommender.")
