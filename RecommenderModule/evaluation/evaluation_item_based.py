from RecommenderModule.recommenders.item_based_recommender import ItemBasedRecommender
from RecommenderModule.evaluation.evaluator import Evaluator

"""This class evaluates item-based collaborative filtering recommenders with
    different parameters, in order for the developer to pick the best parameters
    for the app's item-based recommender."""
class EvaluationItemBased:

    """Evaluate the possible item-based recommenders and print the insights."""
    def run_evaluations(self):

        evaluator = Evaluator()
        parameters_to_evaluate = {
            'min_support': [1, 2, 5, 7],
            'model_function_name': ['cosine', 'msd', 'pearson', 'pearson_baseline']
        }
        recommender = ItemBasedRecommender()
        evaluator.evaluate_all_combinations(recommender, parameters_to_evaluate)
