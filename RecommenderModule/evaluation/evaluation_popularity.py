from RecommenderModule.recommenders.resources.data_provider import DataProvider
from RecommenderModule.recommenders.resources.popular_books_recommender_methods import PopularBooksMethods
from RecommenderModule.evaluation.evaluator import Evaluator

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

    """Evaluate the possible popularity-based recommenders and print the insights."""
    def run_evaluations(self):
        self.evaluator = Evaluator()
        self.trainset, self.testset = self.evaluator.get_train_test_datasets()
        data_provider = DataProvider(filtering_min_ratings_threshold=self.min_ratings_threshold, get_data_from_csv=True)
        recommender_trainset = data_provider.get_filtered_ratings_trainset()
        self.recommender = PopularBooksMethods(trainset=recommender_trainset)
        self.build_read_books_all_users_dict()
        self.evaluate_recommenders()

    """Evaluate the popularity-based recommender using the 3 possible metrics:
        average, median and both."""
    def evaluate_recommenders(self):
        all_recommendations = {}
        recommendations_average = self.get_average_recommendations()
        all_recommendations["Average"] = recommendations_average
        recommendations_median = self.get_median_recommendations()
        all_recommendations["Median"] = recommendations_median
        recommendations_combination = self.get_combination_recommendations()
        all_recommendations["Combination"] = recommendations_combination

        for (scoring_method, recommendations) in all_recommendations.items():
            print(f"\nScoring method: {scoring_method}")
            self.evaluator.evaluate(recommendations)

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


    """Build the read_books_all_users dictionary, which for every user holds 
        an array of all books read by that user."""
    def build_read_books_all_users_dict(self):
        self.read_books_all_users = {}
        trainset = self.trainset
        for inner_user_id, inner_item_id, rating in trainset.all_ratings():
            raw_user_id = trainset.to_raw_uid(inner_user_id)
            raw_item_id = trainset.to_raw_iid(inner_item_id)
            try:
                self.read_books_all_users[raw_user_id].append(raw_item_id)
            except:
                self.read_books_all_users[raw_user_id] = [raw_item_id]