from RecommenderModule.evaluation.resources.evaluation_metrics import EvaluationMetrics
from RecommenderModule.recommenders.resources.data_provider import DataProvider
from RecommenderModule.evaluation.resources.evaluation_data_provider import EvaluationDataProvider
import itertools as it

"""This class allows the developer to evaluate recommenders, using the same train and test sets"""
class Evaluator:

    trainset = None
    testset = []
    evaluation_metrics = None

    def __init__(self, min_ratings_threshold=None, print_status=True):
        self.trainset, self.testset = self.get_train_test_datasets(min_ratings_threshold, print_status)
        self.evaluation_metrics = EvaluationMetrics(self.trainset, self.testset)


    """Get the LeaveOneOut train and test datasets."""
    def get_train_test_datasets(self, min_ratings_threshold=None, print_status=True):
        if self.trainset is None:
            if min_ratings_threshold is None:
                data_provider = DataProvider(get_data_from_csv=True, print_status=print_status)
            else:
                data_provider = DataProvider(get_data_from_csv=True, print_status=print_status, filtering_min_ratings_threshold=min_ratings_threshold)
            dataset = data_provider.get_filtered_ratings_dataset()
            evaluation_data_provider = EvaluationDataProvider(dataset)
            return evaluation_data_provider.get_loocv_datasets()
        else:
            return (self.trainset, self.testset)


    """Evaluate the recommender for all possible combinations of parameters, from the parameters_dict argument
        (parameters_dict contains the parameter name as key and a list of its possible values as value)"""
    def evaluate_all_combinations(self, recommender, parameters_dict):
        all_combinations = self.make_combinations_from_dict(parameters_dict)
        for combination in all_combinations:
            self.evaluate_single_recommender(recommender, combination)


    """Evaluate the recommender, using the given set of parameters"""
    def evaluate_single_recommender(self, recommender, parameters={}):
        print(f"\nEvaluating recommender with parameters: {parameters}")
        recommendations = self.get_recommendations(recommender, parameters)
        self.evaluate(recommendations)  # also calls print_evaluations


    """Get a dictionary of the recommended books for all users in the trainset"""
    def get_recommendations(self, recommender, parameters):
        print("Getting recommendations...")
        recommender.fit(trainset=self.trainset, parameters=parameters)
        recommendations = {}
        nb_users = self.trainset.n_users
        for user_inner_id in self.trainset.all_users():
            if (user_inner_id % 1000 == 0):
                print(f"{user_inner_id} / {nb_users}")
            user_id = self.trainset.to_raw_uid(user_inner_id)
            user_recommendations = recommender.get_user_recommendations(user_id)
            recommendations[user_id] = user_recommendations
        print("Getting recommendations done")
        return recommendations


    """Compute all evaluations for the given recommendations, 
        and then print them through the print_evaluations() method."""
    def evaluate(self, recommendations):
        hit_rate = self.evaluation_metrics.get_hit_rate(recommendations)
        average_reciprocal_hit_rate = self.evaluation_metrics.get_average_reciprocal_hit_rate(recommendations)
        novelty = self.evaluation_metrics.get_novelty(recommendations)
        correct_recommendations_rate = self.evaluation_metrics.get_correct_recommendations_rate(recommendations)
        self.print_evaluations(hit_rate, average_reciprocal_hit_rate, novelty, correct_recommendations_rate)


    """Print the results of the evaluation of the recommender system"""
    def print_evaluations(self, hit_rate, average_reciprocal_hit_rate, novelty, correct_recommendations_rate):
        print()
        print(f" -> hit_rate: {hit_rate}")
        print(f" -> average_reciprocal_hit_rate: {average_reciprocal_hit_rate}")
        print(f" -> novelty: {novelty}")
        print(f" -> correct_recommendations_rate: {correct_recommendations_rate}")
        print()

    """Create a list of all possible combinations of parameters, from the parameters_dict argument
        (parameters_dict contains the parameter name as key and a list of its possible values as value)"""
    def make_combinations_from_dict(self, parameters_dict):
        all_parameter_names = sorted(parameters_dict)
        number_of_parameters = len(all_parameter_names)
        tuples_list = list(it.product(*(parameters_dict[parameter_name] for parameter_name in all_parameter_names)))
        all_combinations = []
        for tuple in tuples_list:
            pairs_list = []
            for i in range(number_of_parameters):
                pairs_list.append((all_parameter_names[i], tuple[i]))
            combination = dict(pairs_list)
            all_combinations.append(combination)
        return all_combinations