"""This file evaluates item-based collaborative filtering recommenders with
    different parameters, in order for the developer to pick the best parameters
    for the app's item-based recommender."""

from RecommenderModule.recommenders.resources.data_provider import DataProvider
from RecommenderModule.evaluation_data_provider import EvaluationDataProvider
from RecommenderModule.recommenders.resources.popular_books_recommender_methods import PopularBooksMethods
from RecommenderModule import evaluator

class EvaluationPopularity:

    trainset = None
    testset = None
    recommender = None
    evaluation_data_provider = None
    read_books_all_users = None

    def run_evaluations(self):

        self.trainset, self.testset = self.get_train_test_datasets()
        self.recommender = PopularBooksMethods(self.trainset)
        self.evaluate_recommenders()


    def get_train_test_datasets(self):
        data_provider = DataProvider(get_data_from_csv=True)
        dataset = data_provider.get_filtered_ratings_dataset()
        self.evaluation_data_provider = EvaluationDataProvider(dataset)
        return self.evaluation_data_provider.get_loocv_datasets()

    def evaluate_recommenders(self):
        self.read_books_all_users = self.evaluation_data_provider.get_read_books_all_users_dict()

        all_recommendations = {}
        recommendations_average = self.get_average_recommendations()
        all_recommendations["Average"] = recommendations_average
        recommendations_median = self.get_median_recommendations()
        all_recommendations["Median"] = recommendations_median
        recommendations_combination = self.get_combination_recommendations()
        all_recommendations["Combination"] = recommendations_combination

        for (scoring_method, recommendations) in all_recommendations.items():

            hit_rate = evaluator.get_hit_rate(recommendations, self.testset)
            average_reciprocal_hit_rate = evaluator.get_average_reciprocal_hit_rate(recommendations, self.testset)
            print(f"Scoring method: {scoring_method}")
            print(f" -> hit_rate:{hit_rate}")
            print(f" -> average_reciprocal_hit_rate:{average_reciprocal_hit_rate}")
            print()

    def get_average_recommendations(self):
        trainset = self.trainset
        recommendations = {}
        for user_inner_id in trainset.all_users():
            user_id = trainset.to_raw_uid(user_inner_id)
            user_read_books = self.read_books_all_users[user_id]
            user_recommendations = self.recommender.get_recommendations_from_average(user_read_books)
            recommendations[user_id] = user_recommendations
        return recommendations

    def get_median_recommendations(self):
        trainset = self.trainset
        recommendations = {}
        for user_inner_id in trainset.all_users():
            user_id = trainset.to_raw_uid(user_inner_id)
            user_read_books = self.read_books_all_users[user_id]
            user_recommendations = self.recommender.get_recommendations_from_median(user_read_books)
            recommendations[user_id] = user_recommendations
        return recommendations

    def get_combination_recommendations(self):
        trainset = self.trainset
        recommendations = {}
        for user_inner_id in trainset.all_users():
            user_id = trainset.to_raw_uid(user_inner_id)
            user_read_books = self.read_books_all_users[user_id]
            user_recommendations = self.recommender.get_recommendations_from_average_and_median(user_read_books)
            recommendations[user_id] = user_recommendations
        return recommendations
