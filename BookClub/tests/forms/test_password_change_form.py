"""Unit tests for the password change form."""
from django.test import TestCase, tag

from BookClub.forms.user_forms import ChangePasswordForm
from BookClub.models import User


@tag('forms', 'user')
class PasswordFormTestCase(TestCase):
    """Changing password form tests"""

    fixtures = ['BookClub/tests/fixtures/default_users.json']

    def setUp(self):
        self.user = User.objects.get(username='johndoe')
        self.form_input = {
            'password': 'Password123',
            'new_password': 'NewPassword123',
            'password_confirmation': 'NewPassword123',
        }

    def test_form_has_necessary_fields(self):
        form = ChangePasswordForm(user=self.user)
        self.assertIn('password', form.fields)
        self.assertIn('new_password', form.fields)
        self.assertIn('password_confirmation', form.fields)

    def test_valid_form(self):
        form = ChangePasswordForm(user=self.user, data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_password_must_contain_uppercase_character(self):
        self.form_input['new_password'] = 'password123'
        self.form_input['password_confirmation'] = 'password123'
        form = ChangePasswordForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_password_must_contain_lowercase_character(self):
        self.form_input['new_password'] = 'PASSWORD123'
        self.form_input['password_confirmation'] = 'PASSWORD123'
        form = ChangePasswordForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_password_must_contain_number(self):
        self.form_input['new_password'] = 'PasswordABC'
        self.form_input['password_confirmation'] = 'PasswordABC'
        form = ChangePasswordForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_new_password_and_password_confirmation_are_identical(self):
        self.form_input['password_confirmation'] = 'WrongPassword123'
        form = ChangePasswordForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_does_not_save_when_user_is_not_provided(self):
        form = ChangePasswordForm(data=self.form_input)
        self.assertFalse(form.is_valid())
        user = form.save()
        self.assertEqual(user, None)
