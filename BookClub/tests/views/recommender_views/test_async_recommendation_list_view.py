from django.urls import reverse
from django.test import TestCase, tag
from BookClub.models import Book, User, Club, UserRecommendations, ClubRecommendations

@tag('async_recommendations')
class AsyncRecommendationListViewsTestCase(TestCase):

    fixtures = [
        "BookClub/tests/fixtures/default_users.json",
        "BookClub/tests/fixtures/default_clubs.json",
        "BookClub/tests/fixtures/default_books.json"
    ]

    def setUp(self):
        self.user1 = User.objects.get(pk=1)
        self.club = Club.objects.get(pk=1)
        self.user_url = reverse('async_user_recommendations')
        self.club_url = reverse('async_club_recommendations', kwargs={'club_url_name': self.club.club_url_name})

    def test_user_url(self):
        self.assertEqual(self.user_url, '/user_recommendations/')

    def test_club_url(self):
        self.assertEqual(self.club_url, '/club_recommendations/Johnathan_Club/')

    def test_correct_template_user_view(self):
        self.client.login(username=self.user1.username, password="Password123")
        response = self.client.get(self.user_url)
        recs = list(UserRecommendations.objects.all())
        self.assertTemplateUsed(response, 'partials/recommendation_list_view.html')

    def test_correct_template_club_view(self):
        self.client.login(username=self.user1.username, password="Password123")
        response = self.client.get(self.club_url)
        self.assertTemplateUsed(response, 'partials/recommendation_list_view.html')

    def test_user_recommendations_are_same_when_not_marked_as_modified(self):
        recommendations = []
        for book in Book.objects.all():
            recommendations.append(book.ISBN)

        user_recommendation = UserRecommendations.objects.create(user=self.user1, recommendations=recommendations, modified=False)
        user_recommendation.save()

        self.client.login(username=self.user1.username, password="Password123")
        response = self.client.get(self.user_url)
        view_recommendations = response.context['recommendations']
        for book in Book.objects.all():
            self.assertIn(book, view_recommendations)

    def test_club_recommendations_are_same_when_not_marked_as_modified(self):
        recommendations = []
        for book in Book.objects.all():
            recommendations.append(book.ISBN)

        user_recommendation = ClubRecommendations.objects.create(club=self.club, recommendations=recommendations, modified=False)
        user_recommendation.save()

        self.client.login(username=self.user1.username, password="Password123")
        response = self.client.get(self.club_url)
        view_recommendations = response.context['recommendations']
        for book in Book.objects.all():
            self.assertIn(book, view_recommendations)
