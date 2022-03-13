from django.contrib import messages
from django.test import TestCase, tag
from django.urls import reverse

from BookClub.forms.user_forms import EditProfileForm
from BookClub.models import User
from BookClub.tests.helpers import reverse_with_query


@tag('user', 'edit_profile')
class EditProfileTestCase(TestCase):
    """ Unit tests for the edit profile view """

    fixtures = [
        'BookClub/tests/fixtures/default_users.json',
    ]

    def setUp(self):
        self.user = User.objects.get(username='johndoe')
        self.url = reverse('edit_profile')
        self.form_input = {
            'username': 'johndoe2',
            'email': 'johndoe2@example.org',
            'public_bio': 'Hello World!',
        }

    def test_profile_url(self):
        self.assertEqual(self.url, '/edit_profile/')

    def test_get_profile(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_profile.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, EditProfileForm))
        self.assertEqual(form.instance, self.user)

    def test_get_profile_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_query('login', query_kwargs={'next': reverse('edit_profile')})
        response = self.client.get(self.url)
        self.assertRedirects(response,
                             redirect_url,
                             status_code=302,
                             target_status_code=200)

    def test_unsuccessful_profile_update(self):
        self.client.login(username=self.user.username, password='Password123')
        self.form_input['username'] = 'BAD_USERNAME!'
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_profile.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, EditProfileForm))
        self.assertTrue(form.is_bound)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'johndoe')
        self.assertEqual(self.user.email, 'johndoe@example.com')
        self.assertEqual(self.user.public_bio, "Hello!")

    def test_unsuccessful_profile_update_due_to_duplicate_username(self):
        self.client.login(username=self.user.username, password='Password123')
        self.form_input['username'] = 'janedoe'
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_profile.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, EditProfileForm))
        self.assertTrue(form.is_bound)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'johndoe')
        self.assertEqual(self.user.email, 'johndoe@example.com')
        self.assertEqual(self.user.public_bio, "Hello!")

    def test_successful_profile_update(self):
        self.client.login(username=self.user.username, password='Password123')
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        response_url = reverse_with_query('user_dashboard')
        self.assertRedirects(response,
                             response_url,
                             status_code=302,
                             target_status_code=200)
        self.assertTemplateUsed(response, 'user_dashboard.html')
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.SUCCESS)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'johndoe2')
        self.assertEqual(self.user.email, 'johndoe2@example.org')
        self.assertEqual(self.user.public_bio, 'Hello World!')

    def test_post_profile_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_query('login', query_kwargs={'next': reverse('edit_profile')})
        response = self.client.post(self.url, self.form_input)
        self.assertRedirects(response,
                             redirect_url,
                             status_code=302,
                             target_status_code=200)
