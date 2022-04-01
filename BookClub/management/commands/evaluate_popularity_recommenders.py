from django.core.management.base import BaseCommand
from RecommenderModule.evaluation.evaluation_popularity import EvaluationPopularity

"""Command to run the evaluations for the popularity recommender."""
class Command(BaseCommand):

        def __init__(self):
            super().__init__()

        def handle(self, *args, **options):
            evaluation_popularity = EvaluationPopularity()
            evaluation_popularity.run_evaluations()
