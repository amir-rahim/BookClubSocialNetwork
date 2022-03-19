from django.test import TestCase, tag
from RecommenderModule.recommenders.resources.item_based_collaborative_filtering_methods import ItemBasedCollaborativeFilteringMethods
from RecommenderModule.recommenders.resources.data_provider import DataProvider
from RecommenderModule.recommenders.resources.library import Library
from BookClub.models import Club, User, ClubMembership

@tag('recommenders')
class ItemBasedRecommenderMethodsTestCase(TestCase):

    def setUp(self):
        data_provider = DataProvider(get_data_from_csv=True)
        self.trainset = data_provider.get_filtered_ratings_trainset()
        self.item_based_methods = ItemBasedCollaborativeFilteringMethods(trainset=self.trainset, print_status=False)
        self.user_id = self.trainset.to_raw_uid(4)
        self.library = Library(trainset=self.trainset)

    def create_club(self):
        club = Club.objects.create(name="Club 1", club_url_name="club_1", description="Test club", is_private=False)
        user1 = User.objects.create(username=self.user_id, email=f"{self.user_id}@kcl.ac.uk", public_bio=f"Hello, I am user {self.user_id}")
        club_membership1 = ClubMembership.objects.create(user=user1, club=club, membership=2)
        user2_id = self.trainset.to_raw_uid(5)
        user2 = User.objects.create(username=user2_id, email=f"{user2_id}@kcl.ac.uk", public_bio=f"Hi, I am {user2_id}")
        club_membership2 = ClubMembership.objects.create(user=user2, club=club, membership=0)
        return club


    def test_get_inner_ratings_from_raw_ratings(self):
        raw_ratings = self.library.get_all_ratings_by_user(self.user_id)
        self.assertEqual(len(raw_ratings), 5)
        inner_items = self.item_based_methods.get_inner_ratings_from_raw_ratings(raw_ratings)
        self.assertEqual(len(raw_ratings), len(inner_items))
        books_rated = [rating[0] for rating in raw_ratings]
        for inner_item, rating in inner_items:
            raw_item_id = self.trainset.to_raw_iid(inner_item)
            self.assertTrue(raw_item_id in books_rated)

    def test_get_inner_ratings_from_raw_ratings_empty_raw_ratings(self):
        inner_ratings = self.item_based_methods.get_inner_ratings_from_raw_ratings([])
        self.assertEqual(inner_ratings, [])

    def test_get_inner_ratings_from_raw_ratings_with_min_rating_parameter(self):
        min_rating = 6
        raw_ratings = self.library.get_all_ratings_by_user(self.user_id)
        inner_items = self.item_based_methods.get_inner_ratings_from_raw_ratings(raw_ratings, min_rating=min_rating)
        self.assertEqual(len(inner_items), 3)
        for inner_item, rating in inner_items:
            self.assertTrue(rating >= min_rating)

    def test_get_recommendations_from_user_inner_ratings_all_ratings(self):
        raw_ratings = self.library.get_all_ratings_by_user(self.user_id)
        all_ratings = self.item_based_methods.get_inner_ratings_from_raw_ratings(raw_ratings)
        recommendations = self.item_based_methods.get_recommendations_from_inner_ratings(ratings=all_ratings)
        self.assertEqual(len(recommendations), 10)
        self.assertEqual(type(recommendations[0]), str)
        for inner_item, rating in all_ratings:
            self.assertFalse(self.trainset.to_raw_iid(inner_item) in recommendations)

    def test_get_recommendations_from_user_inner_ratings_positive_ratings_only(self):
        raw_ratings = self.library.get_all_ratings_by_user(self.user_id)
        all_ratings = self.item_based_methods.get_inner_ratings_from_raw_ratings(raw_ratings)
        positive_ratings = self.item_based_methods.get_inner_ratings_from_raw_ratings(raw_ratings, min_rating=6)
        recommendations = self.item_based_methods.get_recommendations_from_inner_ratings(ratings=positive_ratings, all_books_rated=all_ratings)
        self.assertEqual(len(recommendations), 10)
        self.assertEqual(type(recommendations[0]), str)
        for inner_item, rating in all_ratings:
            self.assertFalse(self.trainset.to_raw_iid(inner_item) in recommendations)

    def test_get_recommendations_all_ratings_from_user_id(self):
        recommendations1 = self.item_based_methods.get_recommendations_all_ratings_from_user_id(self.user_id)
        raw_ratings = self.library.get_all_ratings_by_user(self.user_id)
        all_ratings = self.item_based_methods.get_inner_ratings_from_raw_ratings(raw_ratings)
        recommendations2 = self.item_based_methods.get_recommendations_from_inner_ratings(ratings=all_ratings)
        self.assertEqual(recommendations1, recommendations2)

    def test_get_recommendations_positive_ratings_only_from_user_id(self):
        recommendations1 = self.item_based_methods.get_recommendations_positive_ratings_only_from_user_id(self.user_id)
        raw_ratings = self.library.get_all_ratings_by_user(self.user_id)
        all_ratings = self.item_based_methods.get_inner_ratings_from_raw_ratings(raw_ratings)
        positive_ratings = self.item_based_methods.get_inner_ratings_from_raw_ratings(raw_ratings, min_rating=6)
        recommendations2 = self.item_based_methods.get_recommendations_from_inner_ratings(ratings=positive_ratings, all_books_rated=all_ratings)
        self.assertEqual(recommendations1, recommendations2)

    def test_get_recommendations_positive_ratings_only_from_club_url_name(self):
        club = self.create_club()
        recommendations1 = self.item_based_methods.get_recommendations_positive_ratings_only_from_club_url_name(club.club_url_name)
        raw_ratings = self.library.get_all_ratings_by_club(club.club_url_name)
        all_ratings = self.item_based_methods.get_inner_ratings_from_raw_ratings(raw_ratings)
        positive_ratings = self.item_based_methods.get_inner_ratings_from_raw_ratings(raw_ratings, min_rating=6)
        recommendations2 = self.item_based_methods.get_recommendations_from_inner_ratings(ratings=positive_ratings, all_books_rated=all_ratings)
        self.assertEqual(recommendations1, recommendations2)