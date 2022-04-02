"""Unit testing of the Item Based Recommender"""
from django.test import TestCase, tag

from BookClub.models import Club, User, ClubMembership
from RecommenderModule.recommenders.item_based_recommender import ItemBasedRecommender
from RecommenderModule.recommenders.resources.data_provider import DataProvider
from RecommenderModule.recommenders.resources.item_based_collaborative_filtering_methods import \
    ItemBasedCollaborativeFilteringMethods


@tag('recommenders')
class ItemBasedRecommenderTestCase(TestCase):
    """Item Based Recommender Testing"""
    def setUp(self):
        data_provider = DataProvider(get_data_from_csv=True)
        self.trainset = data_provider.get_filtered_ratings_trainset()
        self.item_based_methods = ItemBasedCollaborativeFilteringMethods(trainset=self.trainset, print_status=False)
        self.item_based_recommender = ItemBasedRecommender()
        self.item_based_recommender.item_based_methods = self.item_based_methods
        self.user_id = self.trainset.to_raw_uid(4)

    def create_club(self):
        club = Club.objects.create(name="Club 1", club_url_name="club_1", description="Test club", is_private=False)
        user1 = User.objects.create(username=self.user_id, email=f"{self.user_id}@kcl.ac.uk", public_bio=f"Hello, I am user {self.user_id}")
        club_membership1 = ClubMembership.objects.create(user=user1, club=club, membership=2)
        user2_id = self.trainset.to_raw_uid(6)
        user2 = User.objects.create(username=user2_id, email=f"{user2_id}@kcl.ac.uk", public_bio=f"Hi, I am {user2_id}")
        club_membership2 = ClubMembership.objects.create(user=user2, club=club, membership=0)
        return club

    def test_get_user_recommendations(self):
        recommendations1 = self.item_based_recommender.get_user_recommendations(self.user_id)
        self.assertEqual(len(recommendations1), 10)
        recommendations2 = self.item_based_methods.get_recommendations_positive_ratings_only_from_user_id(self.user_id)
        self.assertEqual(recommendations1, recommendations2)

    def test_get_user_recommendations_wrong_user_id(self):
        recommendations = self.item_based_recommender.get_user_recommendations("X")
        self.assertEqual(recommendations, [])

    def test_get_club_recommendations(self):
        club = self.create_club()
        recommendations1 = self.item_based_recommender.get_club_recommendations(club.club_url_name)
        self.assertEqual(len(recommendations1), 10)
        recommendations2 = self.item_based_methods.get_recommendations_positive_ratings_only_from_club_url_name(club.club_url_name)
        self.assertEqual(recommendations1, recommendations2)

    def test_get_club_recommendations_wrong_club_url_name(self):
        recommendations = self.item_based_recommender.get_club_recommendations("-")
        self.assertEqual(recommendations, [])

    def test_get_number_of_recommendable_books(self):
        number_of_recommendable_books = self.item_based_recommender.get_number_of_recommendable_books()
        self.assertEqual(number_of_recommendable_books, self.item_based_methods.trainset.n_items)