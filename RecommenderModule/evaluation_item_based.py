"""This file evaluates item-based collaborative filtering recommenders with
    different parameters, in order for the developer to pick the best parameters
    for the app's item-based recommender."""

from RecommenderModule.recommenders.resources.data_provider import DataProvider
from RecommenderModule.evaluation_data_provider import EvaluationDataProvider
from RecommenderModule.recommenders.resources.item_based_collaborative_filtering_methods import ItemBasedCollaborativeFilteringMethods
from RecommenderModule import evaluator

trainset, testset = get_train_test_datasets()
parameters_to_evaluate = {
    'min_support': [2, 5, 10],
    'model_function_name': ['cosine', 'msd', 'pearson', 'pearson_baseline']
}

evaluate_all_combinations(trainset, testset, parameters_to_evaluate)

def get_train_test_datasets():
    data_provider = DataProvider(get_data_from_csv=True)
    dataset = data_provider.get_filtered_ratings_dataset()
    evaluation_data_provider = EvaluationDataProvider(dataset)
    return evaluation_data_provider.get_loocv_datasets()

def evaluate_all_combinations(trainset, testset, parameters_to_evaluate):
    for min_support in parameters_to_evaluate['min_support']:
        for model_function_name in parameters_to_evaluate['model_function_name']:
            recommendations = get_predictions_for_combination(trainset, min_support, model_function_name)
            hit_rate = evaluator.get_hit_rate(recommendations, testset)
            average_reciprocal_hit_rate = evaluator.get_average_reciprocal_hit_rate(recommendations, testset)
            print(f"min_support:{min_support}, model_function_name:{model_function_name}")
            print(f" -> hit_rate:{hit_rate}")
            print(f" -> average_reciprocal_hit_rate:{average_reciprocal_hit_rate}")

def get_predictions_for_combination(trainset, min_support, model_function_name):
    item_based_recommender = ItemBasedCollaborativeFilteringMethods(trainset=trainset, min_support=min_support, model_function_name=model_function_name)
    recommendations = {}
    for user_inner_id in trainset.all_users():
        user_id = trainset.to_raw_uid(user_inner_id)
        user_recommendations = item_based_recommender.get_recommendations_positive_ratings_only_from_user_id(user_id)
        recommendations[user_id] = user_recommendations
    return recommendations
