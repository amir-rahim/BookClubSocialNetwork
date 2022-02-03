"""Tests of the profile view."""

from django.contrib import messages
from django.test import TestCase
from django.urls import reverse
from BookClub.forms import ProfileForm
from BookClub.models import User
from BookClub.tests.helpers import reverse_with_next

class ProfileViewTest(TestCase):
    """Unit tests of the profile view."""

    fixtures = [
        'BookClub/tests/fixtures/default_users.json',
    ]

    def setUp(self):
        self.user = User.objects.get(username='johndoe')
        self.url = reverse('profile')
        self.form_input = {
            'username': 'johndoe2',
            'email': 'johndoe2@example.org',
            'public_bio': 'Hello World!',
        }

    def test_profile_url(self):
        self.assertEqual(self.url, '/profile/')

    def test_get_profile(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'templates/user_dashboard.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, ProfileForm))
        self.assertEqual(form.instance, self.user)

    def test_get_profile_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response,
                             redirect_url,
                             status_code=302,
                             target_status_code=200)

    def test_unsuccesful_profile_update(self):
        self.client.login(email=self.user.email, password='Password123')
        self.form_input['username'] = 'BAD_USERNAME!'
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'templates/user_dashboard.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, ProfileForm))
        self.assertTrue(form.is_bound)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'johndoe')
        self.assertEqual(self.user.email, 'johndoe@example.org')
        self.assertEqual(self.user.public_bio, "Hello, I'm John Doe.")

    def test_unsuccessful_profile_update_due_to_duplicate_username(self):
        self.client.login(email=self.user.email, password='Password123')
        self.form_input['username'] = 'janedoe'
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'templates/user_dashboard.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, ProfileForm))
        self.assertTrue(form.is_bound)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'johndoe')
        self.assertEqual(self.user.email, 'johndoe@example.org')
        self.assertEqual(self.user.public_bio, "Hello, I'm John Doe.")

    def test_succesful_profile_update(self):
        self.client.login(email=self.user.email, password='Password123')
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        response_url = reverse('dashboard')
        self.assertRedirects(response,
                             response_url,
                             status_code=302,
                             target_status_code=200)
        self.assertTemplateUsed(response, 'templates/user_dashboard.html')
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.SUCCESS)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'johndoe2')
        self.assertEqual(self.user.email, 'johndoe2@example.org')
        self.assertEqual(self.user.public_bio, 'New bio')

    def test_post_profile_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.post(self.url, self.form_input)
        self.assertRedirects(response,
                             redirect_url,
                             status_code=302,
                             target_status_code=200)
