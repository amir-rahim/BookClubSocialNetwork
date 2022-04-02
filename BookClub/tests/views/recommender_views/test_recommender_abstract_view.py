"""Unit testing for the Recommender Base view"""
from django.urls import reverse
from django.test import TestCase, tag
from BookClub.models import User, Club


@tag('views', 'recommendations', 'base')
class BaseUserRecommenderViewTestCase(TestCase):
    """Testing for the Recommender Base view"""
    fixtures = [
        "BookClub/tests/fixtures/default_users.json",
        "BookClub/tests/fixtures/default_clubs.json",
    ]

    def setUp(self):
        self.user1 = User.objects.get(pk=1)
        self.club = Club.objects.get(pk=1)
        self.user_url = reverse('user_recommendations')
        self.club_url = reverse('club_recommendations', kwargs={'club_url_name': self.club.club_url_name})

    def test_user_url(self):
        self.assertEqual(self.user_url, '/library/recommendations/')

    def test_club_url(self):
        self.assertEqual(self.club_url, '/club/' + self.club.club_url_name + '/recommendations/')

    def test_correct_template_user_view(self):
        self.client.login(username=self.user1.username, password="Password123")
        response = self.client.get(self.user_url)
        self.assertTemplateUsed(response, 'recommendations/recommendation_base_user.html')

    def test_correct_template_club_view(self):
        self.client.login(username=self.user1.username, password="Password123")
        response = self.client.get(self.club_url)
        self.assertTemplateUsed(response, 'recommendations/recommendation_base_club.html')
