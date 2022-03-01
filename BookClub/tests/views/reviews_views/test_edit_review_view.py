from django.test import TestCase, tag
from django.urls import reverse
from BookClub.models import User, Book, BookReview
from BookClub.tests.helpers import LogInTester, reverse_with_next

@tag('book', 'editreview')
class BookReviewListView(TestCase, LogInTester):
    fixtures = [
        'BookClub/tests/fixtures/default_books.json',
        'BookClub/tests/fixtures/default_users.json',
        'BookClub/tests/fixtures/default_book_reviews.json',
    ]

    def setUp(self):
        # super(TestCase, self).setUp()
        self.book = Book.objects.get(pk=1)
        self.user = User.objects.get(pk=1)
        self.another_user = User.objects.get(pk=2)
        self.book_review = BookReview.objects.get(pk=1)
        self.data = {
            'rating': 10,
            'review': 'Hello there obi wan'
        }

        self.url = reverse('edit_review', kwargs={'book_id': self.book.pk, 'book_review_id': self.book_review.pk})

    # path('library/review/<int:book_id>/edit/<int:book_review_id>/', views.EditReviewView.as_view(), name='edit_review'),
    def test_edit_review_url(self):
        self.assertEqual(self.url, f'/library/review/{self.book.pk}/edit/{self.book_review.pk}/')

    def test_post_edit_review_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.post(self.url, self.data, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200, fetch_redirect_response=True)
        self.assertTemplateUsed(response, 'login.html')

    def test_edit_review_redirects_when_different_user(self):
        self.client.login(username=self.user.username, password="Password123")
        self.assertTrue(self._is_logged_in())
        redirect_url = reverse('book_reviews', kwargs={'book_id': self.book.id})
        response = self.client.post(self.url, self.data, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200, fetch_redirect_response=True)
        self.assertTemplateUsed(response, 'book_reviews.html')

    def test_successful_edit_review_when_logged_in_as_user(self):
        self.client.login(username=self.user.username, password="Password123")
        self.assertTrue(self._is_logged_in())
        response = self.client.post(self.url, self.data)
        redirect_url = reverse('book_reviews', kwargs={'book_id': self.book.id})
        # response_message = self.client.get((redirect_url))
        # messages_list = list(response.context['messages'])
        # self.assertEqual(len(messages_list), 1)
        # self.assertEqual(messages_list[0].level, messages.ERROR)

        self.assertEqual(self.book_review.rating, self.data['rating'])
        self.assertEqual(self.book_review.review, self.data['review'])
        self.assertTemplateUsed(response, 'edit_review.html')
        self.assertRedirects(response, expected_url=redirect_url, status_code=302, target_status_code=200)

    # def test_unsuccessful_edit_review_when_logged_in_as_user(self):
    #
    #
    # def test_edit_review_when_logged_in_and_no_review_made(self):




    # """Unit tests for user being able to delete a meeting"""
    #
    # def test_owner_can_delete_meeting(self):
    #     self.client.login(username=self.owner.username, password="Password123")
    #     self.assertTrue(self._is_logged_in())
    #     meeting_exists_before = Meeting.objects.filter(pk=self.meeting.id).exists()
    #     self.assertEqual(meeting_exists_before, True)
    #     response = self.client.post(self.url)
    #     redirect_url = reverse('meeting_list', kwargs={'club_url_name': self.club.club_url_name})
    #     response_message = self.client.get(redirect_url)
    #     messages_list = list(response_message.context['messages'])
    #     self.assertEqual(len(messages_list), 1)
    #     self.assertEqual(messages_list[0].level, messages.SUCCESS)
    #     self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
    #     meeting_exists_after = Meeting.objects.filter(pk=self.meeting.id).exists()
    #     self.assertEqual(meeting_exists_after, False)
    #
    # def test_organiser_can_delete_meeting(self):
    #     self.client.login(username=self.organiser.username, password="Password123")
    #     self.assertTrue(self._is_logged_in())
    #     meeting_exists_before = Meeting.objects.filter(pk=self.meeting.id).exists()
    #     self.assertEqual(meeting_exists_before, True)
    #     response = self.client.post(self.url)
    #     redirect_url = reverse('meeting_list', kwargs={'club_url_name': self.club.club_url_name})
    #     response_message = self.client.get(redirect_url)
    #     messages_list = list(response_message.context['messages'])
    #     self.assertEqual(len(messages_list), 1)
    #     self.assertEqual(messages_list[0].level, messages.SUCCESS)
    #     self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
    #     meeting_exists_after = Meeting.objects.filter(pk=self.meeting.id).exists()
    #     self.assertEqual(meeting_exists_after, False)
    #
    # """Unit tests for user not being able to delete a valid meeting"""
    #
    # def test_moderator_cannot_delete_meeting(self):
    #     self.client.login(username=self.moderator.username, password="Password123")
    #     self.assertTrue(self._is_logged_in())
    #     meeting_exists_before = Meeting.objects.filter(pk=self.meeting.id).exists()
    #     self.assertEqual(meeting_exists_before, True)
    #     response = self.client.post(self.url)
    #     redirect_url = reverse('meeting_list', kwargs={'club_url_name': self.club.club_url_name})
    #     response_message = self.client.get(redirect_url)
    #     messages_list = list(response_message.context['messages'])
    #     self.assertEqual(len(messages_list), 1)
    #     self.assertEqual(messages_list[0].level, messages.ERROR)
    #     self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
    #     meeting_exists_after = Meeting.objects.filter(pk=self.meeting.id).exists()
    #     self.assertEqual(meeting_exists_before, meeting_exists_after)
    #
    # def test_member_cannot_delete_meeting(self):
    #     self.client.login(username=self.member.username, password="Password123")
    #     self.assertTrue(self._is_logged_in())
    #     meeting_exists_before = Meeting.objects.filter(pk=self.meeting.id).exists()
    #     self.assertEqual(meeting_exists_before, True)
    #     response = self.client.post(self.url)
    #     redirect_url = reverse('meeting_list', kwargs={'club_url_name': self.club.club_url_name})
    #     response_message = self.client.get(redirect_url)
    #     messages_list = list(response_message.context['messages'])
    #     self.assertEqual(len(messages_list), 1)
    #     self.assertEqual(messages_list[0].level, messages.ERROR)
    #     self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
    #     meeting_exists_after = Meeting.objects.filter(pk=self.meeting.id).exists()
    #     self.assertEqual(meeting_exists_before, meeting_exists_after)
    #
    # def test_applicant_cannot_delete_meeting(self):
    #     self.client.login(username=self.applicant.username, password="Password123")
    #     self.assertTrue(self._is_logged_in())
    #     meeting_exists_before = Meeting.objects.filter(pk=self.meeting.id).exists()
    #     self.assertEqual(meeting_exists_before, True)
    #     response = self.client.post(self.url)
    #     redirect_url = reverse('meeting_list', kwargs={'club_url_name': self.club.club_url_name})
    #     response_message = self.client.get(reverse('club_dashboard', kwargs={'club_url_name': self.club.club_url_name}))
    #     messages_list = list(response_message.context['messages'])
    #     self.assertEqual(len(messages_list), 1)
    #     self.assertEqual(messages_list[0].level, messages.ERROR)
    #     self.assertRedirects(response, redirect_url, status_code=302, target_status_code=302)
    #     meeting_exists_after = Meeting.objects.filter(pk=self.meeting.id).exists()
    #     self.assertEqual(meeting_exists_before, meeting_exists_after)
    #
    # """Unit tests for user not being able to delete an invalid meeting"""
    #
    # def test_owner_delete_invalid_meeting(self):
    #     self.client.login(username=self.owner.username, password='Password123')
    #     response = self.client.post(reverse('delete_meeting',
    #                                         kwargs={'club_url_name': self.club.club_url_name,
    #                                                 'meeting_id': self.meeting.id + 9999}))
    #     redirect_url = reverse('meeting_list', kwargs={'club_url_name': self.club.club_url_name})
    #     with self.assertRaises(ObjectDoesNotExist):
    #         Meeting.objects.get(id=self.meeting.id + 9999).exists()
    #     response_message = self.client.get(redirect_url)
    #     messages_list = list(response_message.context['messages'])
    #     self.assertEqual(len(messages_list), 1)
    #     self.assertEqual(messages_list[0].level, messages.ERROR)
    #
    #     self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
    #
    # def test_organiser_delete_invalid_meeting(self):
    #     self.client.login(username=self.organiser.username, password='Password123')
    #     response = self.client.post(reverse('delete_meeting',
    #                                         kwargs={'club_url_name': self.club.club_url_name,
    #                                                 'meeting_id': self.meeting.id + 9999}))
    #     redirect_url = reverse('meeting_list', kwargs={'club_url_name': self.club.club_url_name})
    #     with self.assertRaises(ObjectDoesNotExist):
    #         Meeting.objects.get(id=self.meeting.id + 9999).exists()
    #     response_message = self.client.get(redirect_url)
    #     messages_list = list(response_message.context['messages'])
    #     self.assertEqual(len(messages_list), 1)
    #     self.assertEqual(messages_list[0].level, messages.ERROR)
    #
    #     self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
    #
    # def test_moderator_delete_invalid_meeting(self):
    #     self.client.login(username=self.moderator.username, password='Password123')
    #     response = self.client.post(reverse('delete_meeting',
    #                                         kwargs={'club_url_name': self.club.club_url_name,
    #                                                 'meeting_id': self.meeting.id + 9999}))
    #     redirect_url = reverse('meeting_list', kwargs={'club_url_name': self.club.club_url_name})
    #     with self.assertRaises(ObjectDoesNotExist):
    #         Meeting.objects.get(id=self.meeting.id + 9999).exists()
    #     response_message = self.client.get(redirect_url)
    #     messages_list = list(response_message.context['messages'])
    #     self.assertEqual(len(messages_list), 1)
    #     self.assertEqual(messages_list[0].level, messages.ERROR)
    #
    #     self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
    #
    # def test_member_delete_invalid_meeting(self):
    #     self.client.login(username=self.member.username, password='Password123')
    #     response = self.client.post(reverse('delete_meeting',
    #                                         kwargs={'club_url_name': self.club.club_url_name,
    #                                                 'meeting_id': self.meeting.id + 9999}))
    #     redirect_url = reverse('meeting_list', kwargs={'club_url_name': self.club.club_url_name})
    #     with self.assertRaises(ObjectDoesNotExist):
    #         Meeting.objects.get(id=self.meeting.id + 9999).exists()
    #     response_message = self.client.get(redirect_url)
    #     messages_list = list(response_message.context['messages'])
    #     self.assertEqual(len(messages_list), 1)
    #     self.assertEqual(messages_list[0].level, messages.ERROR)
    #
    #     self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
    #
    # def test_applicant_delete_invalid_meeting(self):
    #     self.client.login(username=self.applicant.username, password='Password123')
    #     response = self.client.post(reverse('delete_meeting',
    #                                         kwargs={'club_url_name': self.club.club_url_name,
    #                                                 'meeting_id': self.meeting.id + 9999}))
    #     redirect_url = reverse('meeting_list', kwargs={'club_url_name': self.club.club_url_name})
    #     with self.assertRaises(ObjectDoesNotExist):
    #         Meeting.objects.get(id=self.meeting.id + 9999).exists()
    #     response_message = self.client.get(reverse('club_dashboard', kwargs={'club_url_name': self.club.club_url_name}))
    #     messages_list = list(response_message.context['messages'])
    #     self.assertEqual(len(messages_list), 1)
    #     self.assertEqual(messages_list[0].level, messages.ERROR)
    #
    #     self.assertRedirects(response, redirect_url, status_code=302, target_status_code=302)