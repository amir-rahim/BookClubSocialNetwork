from RecommenderModule.recommenders.content_based_recommender import ContentBasedRecommender
from RecommenderModule.evaluation.evaluator import Evaluator

"""This class evaluates content-based collaborative filtering recommenders with
    different parameters, in order for the developer to determine the best parameters
    for the app's content-based recommender."""
class EvaluationContentBased:

    """Evaluate the possible content-based recommenders and print the insights."""
    def run_evaluations(self):

        evaluator = Evaluator()
        parameters_to_evaluate = {
            'using_publication_year': [True, False],
        }
        recommender = ContentBasedRecommender()
        evaluator.evaluate_all_combinations(recommender, parameters_to_evaluate)
