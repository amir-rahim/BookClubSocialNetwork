from django.urls import reverse
from django.test import TestCase, tag
from BookClub.models import Book, User, Club, BookReview, UserRecommendations, ClubRecommendations

from RecommenderModule import recommendations_provider
from RecommenderModule.recommenders.resources.item_based_collaborative_filtering_methods import ItemBasedCollaborativeFilteringMethods

@tag('async_recommendations')
class AsyncRecommendationListViewsTestCase(TestCase):

    fixtures = [
        "BookClub/tests/fixtures/default_users.json",
        "BookClub/tests/fixtures/default_clubs.json",
        "BookClub/tests/fixtures/default_books.json",
        "BookClub/tests/fixtures/default_club_members.json"
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

    def test_user_gets_personalised_recommendations_when_more_than_3_available(self):
        trainset = ItemBasedCollaborativeFilteringMethods().trainset
        i = 0
        for book in trainset.all_items():
            book_isbn = trainset.to_raw_iid(book)
            book1 = Book.objects.create(title=f"Book {i}", ISBN=book_isbn, author="John Doe",
                                        publicationYear="2002-02-02", publisher="Penguin")
            review1 = BookReview.objects.create(creator=self.user1, book=book1, book_rating=7)
            i += 1
            if i >= 10:
                break
        personalised_recommendations = recommendations_provider.get_user_personalised_recommendations(self.user1.username)

        # The loop below is populating the database with Book objects
        # using the recommended isbn values, so that the view can extra info besides the isbn
        i = 0
        for isbn in personalised_recommendations:
            book1 = Book.objects.create(title=f"Book {i}", ISBN=isbn, author="John Doe",
                                        publicationYear="2002-02-02", publisher="Penguin")
            i += 1

        self.client.login(username=self.user1.username, password="Password123")
        response = self.client.get(self.user_url)
        view_recommendations = response.context['recommendations']


        view_recommendations_isbns = []
        for rec in view_recommendations:
            view_recommendations_isbns.append(rec.ISBN)


        for book in personalised_recommendations:
            self.assertIn(book, view_recommendations_isbns)

    def test_club_gets_personalised_recommendations_when_more_than_3_available(self):
        trainset = ItemBasedCollaborativeFilteringMethods().trainset
        i = 0
        for book in trainset.all_items():
            book_isbn = trainset.to_raw_iid(book)
            book1 = Book.objects.create(title=f"Book {i}", ISBN=book_isbn, author="John Doe",
                                        publicationYear="2002-02-02", publisher="Penguin")
            review1 = BookReview.objects.create(creator=self.user1, book=book1, book_rating=7)
            i += 1
            if i >= 10:
                break
        personalised_recommendations = recommendations_provider.get_club_personalised_recommendations(self.club.club_url_name)
        self.assertEqual(len(personalised_recommendations), 10)
        self.assertEqual(type(personalised_recommendations[0]), str)


        # The loop below is populating the database with Book objects
        # using the recommended isbn values, so that the view can extra info besides the isbn
        i = 0
        for isbn in personalised_recommendations:
            book1 = Book.objects.create(title=f"Book {i}", ISBN=isbn, author="John Doe",
                                        publicationYear="2002-02-02", publisher="Penguin")
            i += 1

        self.client.login(username=self.user1.username, password="Password123")
        response = self.client.get(self.club_url)
        view_recommendations = response.context['recommendations']


        view_recommendations_isbns = []
        for rec in view_recommendations:
            view_recommendations_isbns.append(rec.ISBN)


        for book in personalised_recommendations:
            self.assertIn(book, view_recommendations_isbns)
