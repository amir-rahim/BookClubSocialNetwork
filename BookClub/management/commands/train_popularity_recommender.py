from django.core.management.base import BaseCommand
from BookClub.recommender_module import recommendations_provider

class Command(BaseCommand):
        """Train and save popularity lists for popularity recommender."""
        def __init__(self):
            super().__init__()

        def handle(self, *args, **options):
            print("Started training popularity recommender...")
            recommendations_provider.retrain_popularity_recommender()
