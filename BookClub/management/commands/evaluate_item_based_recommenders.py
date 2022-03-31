from django.core.management.base import BaseCommand
from RecommenderModule.evaluation.evaluation_item_based import EvaluationItemBased

"""Command to run the evaluations for the item-based recommender."""
class Command(BaseCommand):

        def __init__(self):
            super().__init__()

        def handle(self, *args, **options):
            evaluation_item_based = EvaluationItemBased()
            evaluation_item_based.run_evaluations()
