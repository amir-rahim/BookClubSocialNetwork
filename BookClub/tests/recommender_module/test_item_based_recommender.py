from django.test import TestCase, tag
from RecommenderModule.recommenders.item_based_recommender import ItemBasedRecommender
from RecommenderModule.recommenders.resources.data_provider import DataProvider
from RecommenderModule.recommenders.resources.item_based_collaborative_filtering_methods import ItemBasedCollaborativeFilteringMethods

@tag('recommenders')
class RecommendationsProviderTestCase(TestCase):

    def setUp(self):
        data_provider = DataProvider(get_data_from_csv=True)
        trainset = data_provider.get_filtered_ratings_trainset()
        self.item_based_methods = ItemBasedCollaborativeFilteringMethods(trainset=trainset, print_status=False)
        self.item_based_recommender = ItemBasedRecommender()
        self.item_based_recommender.item_based_methods = self.item_based_methods
        self.user_id = trainset.to_raw_uid(4)

    def test_get_recommendations(self):
        recommendations1 = self.item_based_recommender.get_recommendations(self.user_id)
        self.assertEqual(len(recommendations1), 10)
        recommendations2 = self.item_based_methods.get_recommendations_positive_ratings_only_from_user_id(self.user_id)
        self.assertEqual(recommendations1, recommendations2)

    def test_get_recommendations_wrong_user_id(self):
        recommendations = self.item_based_recommender.get_recommendations("X")
        self.assertEqual(recommendations, [])