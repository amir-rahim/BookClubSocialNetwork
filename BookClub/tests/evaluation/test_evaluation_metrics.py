from django.test import TestCase, tag
from RecommenderModule.recommenders.resources.data_provider import DataProvider
from RecommenderModule.evaluation.resources.evaluation_data_provider import EvaluationDataProvider
from RecommenderModule.evaluation.resources.evaluation_metrics import EvaluationMetrics
from collections import Counter

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

    def test_get_correct_recommendations_rate_100_percent_rate(self):
        test_recommendations = self.build_test_recommendations()
        for key in test_recommendations.keys():
            test_recommendations[key].insert(0, "XXXXXXXXXX")
            break
        correct_recommendations_rate = self.evaluation_metrics.get_correct_recommendations_rate(test_recommendations)
        recommendations_length = 0
        for user_recommendations in test_recommendations.values():
            recommendations_length += len(user_recommendations)
        self.assertEqual(correct_recommendations_rate, (recommendations_length-1)/recommendations_length)