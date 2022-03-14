from RecommenderModule.recommenders.resources.data_provider import DataProvider
from RecommenderModule.evaluation.resources.evaluation_data_provider import EvaluationDataProvider
from RecommenderModule.recommenders.resources.popular_books_recommender_methods import PopularBooksMethods
from RecommenderModule.evaluation.resources import evaluator

"""This file evaluates popularity-based recommenders according to the different
    metrics (average, median, both), in order for the developer to pick the best
    parameters for the app's popularity-based recommender."""
class EvaluationPopularity:

    trainset = None
    testset = None
    recommender = None
    evaluation_data_provider = None
    read_books_all_users = None

    def __init__(self, min_ratings_threshold=300):
        self.min_ratings_threshold = min_ratings_threshold

    """Evaluate the possible popularity-based recommenders and print the insights."""
    def run_evaluations(self):

        self.trainset, self.testset = self.get_train_test_datasets()
        self.recommender = PopularBooksMethods(trainset=self.trainset)
        self.evaluate_recommenders()


    """Get the LeaveOneOut train and test datasets."""
    def get_train_test_datasets(self):
        data_provider = DataProvider(get_data_from_csv=True, filtering_min_ratings_threshold=self.min_ratings_threshold)
        dataset = data_provider.get_filtered_ratings_dataset()
        self.evaluation_data_provider = EvaluationDataProvider(dataset)
        return self.evaluation_data_provider.get_loocv_datasets()

    """Evaluate the popularity-based recommender using the 3 possible metrics:
        average, median and both."""
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
            print()
            print(f"Scoring method: {scoring_method}")
            print(f" -> hit_rate:{hit_rate}")
            print(f" -> average_reciprocal_hit_rate:{average_reciprocal_hit_rate}")
            print()

    """Get the recommendations for all users from the train set, using the
        average metric."""
    def get_average_recommendations(self):
        trainset = self.trainset
        recommendations = {}
        for user_inner_id in trainset.all_users():
            user_id = trainset.to_raw_uid(user_inner_id)
            user_read_books = self.read_books_all_users[user_id]
            user_recommendations = self.recommender.get_recommendations_from_average(user_read_books)
            recommendations[user_id] = user_recommendations
        return recommendations

    """Get the recommendations for all users from the train set, using the
        median metric."""
    def get_median_recommendations(self):
        trainset = self.trainset
        recommendations = {}
        for user_inner_id in trainset.all_users():
            user_id = trainset.to_raw_uid(user_inner_id)
            user_read_books = self.read_books_all_users[user_id]
            user_recommendations = self.recommender.get_recommendations_from_median(user_read_books)
            recommendations[user_id] = user_recommendations
        return recommendations

    """Get the recommendations for all users from the train set, using a
        combination of the average and median metrics."""
    def get_combination_recommendations(self):
        trainset = self.trainset
        recommendations = {}
        for user_inner_id in trainset.all_users():
            user_id = trainset.to_raw_uid(user_inner_id)
            user_read_books = self.read_books_all_users[user_id]
            user_recommendations = self.recommender.get_recommendations_from_average_and_median(user_read_books)
            recommendations[user_id] = user_recommendations
        return recommendations
