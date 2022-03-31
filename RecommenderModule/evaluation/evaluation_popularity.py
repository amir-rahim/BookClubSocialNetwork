from RecommenderModule.recommenders.resources.data_provider import DataProvider
from RecommenderModule.recommenders.resources.popular_books_recommender_methods import PopularBooksMethods
from RecommenderModule.evaluation.evaluator import Evaluator
from RecommenderModule.recommenders.popular_books_recommender import PopularBooksRecommender

"""This file evaluates popularity-based recommenders according to the different
    metrics (average, median, both), in order for the developer to pick the best
    parameters for the app's popularity-based recommender."""
class EvaluationPopularity:

    trainset = None
    testset = None
    evaluator = None
    recommender = None
    evaluation_data_provider = None
    read_books_all_users = {}

    def __init__(self, min_ratings_threshold=300):
        self.min_ratings_threshold = min_ratings_threshold

    """Evaluate the possible popularity recommenders and print the insights."""
    def run_evaluations(self):

        evaluator = Evaluator()
        parameters_to_evaluate = {
            'min_ratings_threshold': [100, 200, 300],
            'ranking_method': ['average', 'median', 'combination']
        }
        recommender = PopularBooksRecommender()
        evaluator.evaluate_all_combinations(recommender, parameters_to_evaluate)
