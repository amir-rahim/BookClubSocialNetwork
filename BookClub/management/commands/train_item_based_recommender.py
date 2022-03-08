from django.core.management.base import BaseCommand
from BookClub.recommender_module import recommendations_provider

class Command(BaseCommand):
        """Train and save item-based collaborative filtering model for item-based recommender."""
        def __init__(self):
            super().__init__()

        def handle(self, *args, **options):
            print("Started training item-based recommender...")
            recommendations_provider.retrain_item_based_recommender()
