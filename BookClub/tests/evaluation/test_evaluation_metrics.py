from django.test import TestCase, tag
from RecommenderModule.recommenders.resources.data_provider import DataProvider
from RecommenderModule.evaluation.resources.evaluation_data_provider import EvaluationDataProvider
from RecommenderModule.evaluation.resources.evaluation_metrics import EvaluationMetrics
from collections import Counter
from RecommenderModule.recommenders.popular_books_recommender import PopularBooksRecommender

@tag('evaluation')
class EvaluationMetricsTestCase(TestCase):

    def setUp(self):
        data_provider = DataProvider(get_data_from_csv=True, print_status=False)
        evaluation_data_provider = EvaluationDataProvider(data_provider.get_filtered_ratings_dataset())
        self.trainset, self.testset = evaluation_data_provider.get_loocv_datasets()
        self.evaluation_metrics = EvaluationMetrics(self.trainset, self.testset)

    def build_test_recommendations(self):
        test_recommendations = {}
        for user_id, book_isbn, rating in self.testset[:100]:
            try:
                test_recommendations[user_id].append(book_isbn)
            except:
                test_recommendations[user_id] = [book_isbn]
        return test_recommendations

    def test_compute_list_books_sorted_by_most_read(self):
        popularity_list = self.evaluation_metrics.popularity_list
        all_book_occurrences = []
        for user_inner_id, item_inner_id, rating in self.trainset.all_ratings():
            all_book_occurrences.append(self.trainset.to_raw_iid(item_inner_id))
        counter = Counter(all_book_occurrences)
        for i in range(1, len(popularity_list)):
            book1 = popularity_list[i-1]
            book2 = popularity_list[i]
            self.assertTrue(counter[book1] >= counter[book2])

    def test_get_hit_rate(self):
        test_recommendations = self.build_test_recommendations()
        hit_rate = self.evaluation_metrics.get_hit_rate(test_recommendations)
        self.assertEqual(hit_rate, 100/len(self.testset))

    def test_get_average_reciprocal_hit_rate(self):
        test_recommendations = self.build_test_recommendations()
        for key in test_recommendations.keys():
            test_recommendations[key].insert(0, "XXXXXXXXXX")
            break
        hit_rate = self.evaluation_metrics.get_hit_rate(test_recommendations)
        self.assertEqual(hit_rate, 100/len(self.testset))
        average_reciprocal_hit_rate = self.evaluation_metrics.get_average_reciprocal_hit_rate(test_recommendations)
        self.assertTrue(average_reciprocal_hit_rate < 100/len(self.testset))
        self.assertTrue(average_reciprocal_hit_rate > 0)

    def test_get_novelty(self):
        popularity_list = self.evaluation_metrics.popularity_list
        test_recommendations = {
            "user 1": [popularity_list[0], popularity_list[1]],
            "user 2": [popularity_list[2]],
            "user 3": [popularity_list[3], popularity_list[4], popularity_list[5]]
        }
        novelty = self.evaluation_metrics.get_novelty(test_recommendations)
        self.assertEqual(novelty, 21/6)

    def test_get_precision(self):
        test_recommendations = self.build_test_recommendations()
        for key in test_recommendations.keys():
            test_recommendations[key].insert(0, "XXXXXXXXXX")
            break
        precision = self.evaluation_metrics.get_precision(test_recommendations)
        recommendations_length = 0
        for user_recommendations in test_recommendations.values():
            recommendations_length += len(user_recommendations)
        self.assertEqual(precision, (recommendations_length-1)/recommendations_length)

    def test_get_precision_100_percents(self):
        test_recommendations = self.build_test_recommendations()
        precision = self.evaluation_metrics.get_precision(test_recommendations)
        self.assertEqual(precision, 1)

    def test_get_recommendations_eligible_users_rate(self):
        test_recommendations = self.build_test_recommendations()
        all_users = self.trainset.n_users
        recommendation_eligible_users_rate = self.evaluation_metrics.get_recommendation_eligible_users_rate(test_recommendations)
        self.assertEqual(recommendation_eligible_users_rate, len(test_recommendations) / all_users)

    def test_get_user_coverage(self):
        test_recommendations = self.build_test_recommendations()
        good_recommendation_users = set()
        for user_id, book_id, rating in self.testset:
            try:
                if book_id in test_recommendations[user_id]:
                    good_recommendation_users.add(user_id)
            except:
                pass
        user_coverage = self.evaluation_metrics.get_user_coverage(test_recommendations)
        self.assertEqual(user_coverage, len(good_recommendation_users)/len(test_recommendations))

    def test_get_f1_score(self):
        test_recommendations = self.build_test_recommendations()
        f1_score_1 = self.evaluation_metrics.get_f1_score(test_recommendations)
        precision = self.evaluation_metrics.get_precision(test_recommendations)
        recall = self.evaluation_metrics.get_hit_rate(test_recommendations)
        f1_score_2 = 2 * (precision * recall) / (precision + recall)
        self.assertEqual(f1_score_1, f1_score_2)

    def test_get_book_coverage(self):
        test_recommender = PopularBooksRecommender()
        test_recommender.fit(self.trainset)
        book_coverage_1 = self.evaluation_metrics.get_book_coverage(test_recommender)
        book_coverage_2 = len(test_recommender.popular_books_methods.filtered_books_list) / self.trainset.n_items
        self.assertEqual(book_coverage_1, book_coverage_2)