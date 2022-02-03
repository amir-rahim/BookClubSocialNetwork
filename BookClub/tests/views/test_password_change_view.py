"""Tests for the password change view."""

from django.contrib.auth.hashers import check_password
from django.test import TestCase
from django.urls import reverse
from BookClub.forms.user_forms import ChangePasswordForm
from BookClub.models import User
from BookClub.tests.helpers import reverse_with_query


class PasswordViewTest(TestCase):
    """Unit tests for the password change view."""

    fixtures = ['BookClub/tests/fixtures/default_users.json']

    def setUp(self):
        self.user = User.objects.get(username='johndoe')
        self.url = reverse('password_change')
        self.form_input = {
            'password': 'Password123',
            'new_password': 'NewPassword123',
            'password_confirmation': 'NewPassword123',
        }

    def test_password_url(self):
        self.assertEqual(self.url, '/password_change/')

    def test_get_password(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'templates/password_change.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, ChangePasswordForm))

    def test_get_password_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_query('login')
        response = self.client.get(self.url)
        self.assertRedirects(response,
                             redirect_url,
                             status_code=302,
                             target_status_code=200)

    def test_successful_password_change(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.post(self.url, self.form_input, follow=True)
        response_url = reverse('user_dashboard')
        self.assertRedirects(response,
                             response_url,
                             status_code=302,
                             target_status_code=200)
        self.assertTemplateUsed(response, 'templates/user_dashboard.html')
        self.user.refresh_from_db()
        is_password_correct = check_password('NewPassword123',
                                             self.user.password)
        self.assertTrue(is_password_correct)

    def test_password_change_unsuccessful_without_correct_old_password(self):
        self.client.login(email=self.user.email, password='Password123')
        self.form_input['password'] = 'WrongPassword123'
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'templates/password_change.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, ChangePasswordForm))
        self.user.refresh_from_db()
        is_password_correct = check_password('Password123', self.user.password)
        self.assertTrue(is_password_correct)

    def test_password_change_unsuccessful_without_password_confirmation(self):
        self.client.login(email=self.user.email, password='Password123')
        self.form_input['password_confirmation'] = 'WrongPassword123'
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'templates/password_change.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, ChangePasswordForm))
        self.user.refresh_from_db()
        is_password_correct = check_password('Password123', self.user.password)
        self.assertTrue(is_password_correct)

    def test_password_change_unsuccessful_password_confirmation_not_matching(
            self):
        self.client.login(email=self.user.email, password='Password123')
        self.form_input['new_password'] = 'Newpassword123'
        self.form_input['password_confirmation'] = 'WrongPassword123'
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'templates/password_change.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, ChangePasswordForm))
        self.user.refresh_from_db()
        is_password_correct = check_password('Password123', self.user.password)
        self.assertTrue(is_password_correct)

    def test_post_profile_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_query('login')
        response = self.client.post(self.url, self.form_input)
        self.assertRedirects(response,
                             redirect_url,
                             status_code=302,
                             target_status_code=200)
        is_password_correct = check_password('Password123', self.user.password)
        self.assertTrue(is_password_correct)
