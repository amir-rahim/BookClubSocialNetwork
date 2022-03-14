from RecommenderModule.recommenders.resources.data_provider import DataProvider
from RecommenderModule.evaluation.resources.evaluation_data_provider import EvaluationDataProvider
from RecommenderModule.recommenders.resources.item_based_collaborative_filtering_methods import ItemBasedCollaborativeFilteringMethods
from RecommenderModule.evaluation.resources import evaluator

"""This class evaluates item-based collaborative filtering recommenders with
    different parameters, in order for the developer to pick the best parameters
    for the app's item-based recommender."""
class EvaluationItemBased:

    trainset = None
    testset = None

    """Evaluate the possible item-based recommenders and print the insights."""
    def run_evaluations(self):

        self.trainset, self.testset = self.get_train_test_datasets()
        parameters_to_evaluate = {
            'min_support': [2, 5, 10],
            'model_function_name': ['cosine', 'msd', 'pearson', 'pearson_baseline']
        }

        self.evaluate_all_combinations(parameters_to_evaluate)


    """Get the LeaveOneOut train and test datasets."""
    def get_train_test_datasets(self):
        data_provider = DataProvider(get_data_from_csv=True)
        dataset = data_provider.get_filtered_ratings_dataset()
        evaluation_data_provider = EvaluationDataProvider(dataset)
        return evaluation_data_provider.get_loocv_datasets()

    """Evaluate the item-based recommender with all possible combinations of
        passed parameters."""
    def evaluate_all_combinations(self, parameters_to_evaluate):
        for min_support in parameters_to_evaluate['min_support']:
            for model_function_name in parameters_to_evaluate['model_function_name']:
                recommendations = self.get_recommendations_for_combination(min_support, model_function_name)
                hit_rate = evaluator.get_hit_rate(recommendations, self.testset)
                average_reciprocal_hit_rate = evaluator.get_average_reciprocal_hit_rate(recommendations, self.testset)
                novelty = evaluator.get_novelty(recommendations, self.trainset)
                print()
                print(f"min_support:{min_support}, model_function_name:{model_function_name}")
                print(f" -> hit_rate:{hit_rate}")
                print(f" -> average_reciprocal_hit_rate:{average_reciprocal_hit_rate}")
                print(f" -> novelty:{novelty}")
                print()

    """Get the recommendations for all users from the train set, for the given
        parameters combination."""
    def get_recommendations_for_combination(self, min_support, model_function_name):
        print("Getting recommendations...")
        item_based_recommender = ItemBasedCollaborativeFilteringMethods(trainset=self.trainset, min_support=min_support, model_function_name=model_function_name)
        recommendations = {}
        nb_users = self.trainset.n_users
        for user_inner_id in self.trainset.all_users():
            if (user_inner_id % 1000 == 0):
                print(f"{user_inner_id} / {nb_users}")
            user_id = self.trainset.to_raw_uid(user_inner_id)
            user_recommendations = item_based_recommender.get_recommendations_positive_ratings_only_from_user_id(user_id)
            recommendations[user_id] = user_recommendations
        print("Getting recommendations done")
        return recommendations
