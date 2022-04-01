from django.core.management.base import BaseCommand
from RecommenderModule.evaluation.evaluation_content_based import EvaluationContentBased

"""Command to run the evaluations for the content-based recommender."""
class Command(BaseCommand):

        def __init__(self):
            super().__init__()

        def handle(self, *args, **options):
            evaluation_content_based = EvaluationContentBased()
            evaluation_content_based.run_evaluations()
