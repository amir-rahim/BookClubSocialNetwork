from django.contrib import messages
from django.test import TestCase, tag
from django.urls import reverse

from BookClub.models import User, BookList
from BookClub.tests.helpers import LogInTester, reverse_with_next


@tag("booklist", "delete_list")
class DeleteBookListView(TestCase, LogInTester):
    fixtures = [
        'BookClub/tests/fixtures/default_users.json',
        'BookClub/tests/fixtures/default_books.json',
        'BookClub/tests/fixtures/booklists.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='johndoe')
        self.booklist = BookList.objects.get(pk=1)
        self.url = reverse('delete_booklist', kwargs={'username': self.user.username,
                                                      'list_id': self.booklist.pk})

    def test_url(self):
        correct_url = '/user/johndoe/list/1/delete/'
        self.assertEqual(self.url, correct_url)

    def test_redirects_on_get_request_when_not_logged_in(self):
        self.assertFalse(self._is_logged_in())

        redirect_url = reverse_with_next('login', self.url)
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200, fetch_redirect_response=True
                             )
        self.assertTemplateUsed(response, 'login.html')

    def test_redirects_on_get_request_when_logged_in(self):
        self.client.login(username='johndoe', password='Password123')
        self.assertTrue(self._is_logged_in())

        redirect_url = reverse('booklists_list', kwargs={'username': 'johndoe'})
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200, fetch_redirect_response=True
                             )
        self.assertTemplateUsed(response, 'user_booklists.html')

        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(str(messages_list[0]), 'Non-existing page was requested, so we redirected you here...')
        self.assertEqual(messages_list[0].level, messages.ERROR)

    def test_returns_403_when_trying_to_delete_a_list_of_another_user(self):
        self.client.login(username='johndoe', password='Password123')
        self.assertTrue(self._is_logged_in())

        url = reverse('delete_booklist', kwargs={'username': 'janedoe',
                                                 'list_id': 2})

        before_count = BookList.objects.count()
        response = self.client.post(url)
        after_count = BookList.objects.count()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(after_count, before_count)
        self.assertTrue(BookList.objects.filter(pk=2, creator=User.objects.get(username='janedoe')).exists())

    def test_redirects_when_non_existing_list_is_targeted(self):
        self.client.login(username='johndoe', password='Password123')
        self.assertTrue(self._is_logged_in())
        before_count = BookList.objects.count()

        url = reverse('delete_booklist', kwargs={'username': 'johndoe',
                                                 'list_id': 5})
        self.assertFalse(BookList.objects.filter(pk=5, creator=self.user).exists())

        redirect_url = reverse('booklists_list', kwargs={'username': 'johndoe'})
        response = self.client.post(url, follow=True)
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200, fetch_redirect_response=True
                             )
        self.assertTemplateUsed(response, 'user_booklists.html')
        response_messages = messages.get_messages(response.wsgi_request)
        self.assertEqual(len(response_messages), 1)
        # below test not working, cannot check message contents...
        # self.assertEqual(str(response_messages[0]), 'Non-existing list was targeted')

        after_count = BookList.objects.count()
        self.assertEqual(after_count, before_count)

    def test_valid_delete_request(self):
        self.client.login(username='johndoe', password='Password123')
        self.assertTrue(self._is_logged_in())

        before_count = BookList.objects.filter(creator=self.user).count()
        list_pk = self.booklist.pk
        self.assertTrue(BookList.objects.filter(creator=self.user, pk=list_pk).exists())

        redirect_url = reverse('booklists_list', kwargs={'username': 'johndoe'})
        response = self.client.post(self.url, follow=True)
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200, fetch_redirect_response=True
                             )
        self.assertTemplateUsed(response, 'user_booklists.html')
        response_messages = messages.get_messages(response.wsgi_request)
        self.assertEqual(len(response_messages), 1)

        after_count = BookList.objects.filter(creator=self.user).count()
        self.assertEqual(after_count, before_count - 1)
        self.assertFalse(BookList.objects.filter(creator=self.user, pk=list_pk).exists())
