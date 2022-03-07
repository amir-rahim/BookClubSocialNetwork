from django.test import TestCase, tag
from django.urls import reverse
from BookClub.models import User, BookList
from BookClub.forms.booklist_forms import CreateBookListForm
from BookClub.tests.helpers import reverse_with_next

from datetime import date

@tag('createbooklist')
@tag('booklist')
class CreateBooklistViewTestcase(TestCase):
    fixtures = [
        "BookClub/tests/fixtures/default_users.json",
        "BookClub/tests/fixtures/booklists.json",
        "BookClub/tests/fixtures/default_books.json"
    ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.user = User.objects.get(username='johndoe')
        self.url = reverse('create_booklist', kwargs={'username':self.user.username})
        self.data = {
            'title': 'Booklist 1',
            'description': 'Booklist of John',
        }

    def test_create_club_url(self):
        self.assertEqual(self.url, f'/user/{self.user.username}/lists/create')

    def test_post_create_booklist_redirects_when_not_logged_in(self):
        booklist_count_before = BookList.objects.count()
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.post(self.url, self.data, follow=True)
        self.assertRedirects(response, redirect_url,
            status_code=302, target_status_code=200, fetch_redirect_response=True
        )
        self.assertTemplateUsed(response, 'login.html')
        booklist_count_after = BookList.objects.count()
        self.assertEqual(booklist_count_after, booklist_count_before)

    def test_get_create_booklist_redirects_when_not_logged_in(self):
        booklist_count_before = BookList.objects.count()
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url,
            status_code=302, target_status_code=200, fetch_redirect_response=True
        )
        self.assertTemplateUsed(response, 'login.html')
        booklist_count_after = BookList.objects.count()
        self.assertEqual(booklist_count_after, booklist_count_before)

    def test_get_create_booklist(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_booklist.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, CreateBookListForm))
        self.assertFalse(form.is_bound)

    def test_unsuccessful_create_booklist(self):
        self.client.login(username=self.user.username, password='Password123')
        self.data['title'] = ''
        before_count = BookList.objects.count()
        response = self.client.post(self.url, self.data)
        after_count = BookList.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_booklist.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, CreateBookListForm))
        self.assertTrue(form.is_bound)

    def test_successful_create_booklist(self):
        self.client.login(username=self.user.username, password='Password123')
        before_count = BookList.objects.count()
        saving_date = date.today()
        response = self.client.post(self.url, self.data, follow=True)
        booklist = BookList.objects.get(title = self.data['title'])
        after_count = BookList.objects.count()
        self.assertEqual(after_count, before_count+1)
        response_url = reverse('booklists_list', kwargs={'username': self.user.username})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_booklists.html')
        self.assertEqual(booklist.title, self.data['title'])
        self.assertEqual(booklist.description, self.data['description'])
        self.assertEqual(booklist.creator, self.user)
        self.assertEqual(booklist.created_on, saving_date)