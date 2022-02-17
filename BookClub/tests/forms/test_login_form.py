"""Unit tests of the log in form."""
from django import forms
from django.test import TestCase, tag
from BookClub.forms import LogInForm

@tag('auth','user')
class LogInFormTestCase(TestCase):
    """Unit tests of the log in form."""
    def setUp(self):
        self.form_input = {'username': 'janedoe', 'password': 'Password123'}

    def test_form_contains_required_fields(self):
        form = LogInForm()
        password_field = form.fields['password']

        self.assertIn('username', form.fields)
        self.assertIn('password', form.fields)

        self.assertTrue(isinstance(password_field.widget,forms.PasswordInput))

    def test_form_accepts_valid_input(self):
        form = LogInForm(data=self.form_input)

        self.assertTrue(form.is_valid())

    def test_form_rejects_blank_username(self):
        form = LogInForm(data=self.form_input)

        self.form_input['username'] = ''

        self.assertFalse(form.is_valid())

    def test_form_rejects_blank_password(self):
        self.form_input['password'] = ''
        form = LogInForm(data=self.form_input)

        self.assertFalse(form.is_valid())

    def test_form_accepts_incorrect_username(self):
        self.form_input['username'] = 'ja'
        form = LogInForm(data=self.form_input)

        self.assertTrue(form.is_valid())

    def test_form_accepts_incorrect_password(self):
        self.form_input['password'] = 'pwd'
        form = LogInForm(data=self.form_input)
        
        self.assertTrue(form.is_valid())