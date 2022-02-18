"""Tests of the update user details form."""

from django import forms
from django.test import TestCase, tag
from django.urls import reverse
from BookClub.forms.user_forms import EditProfileForm
from BookClub.models import User
@tag('editprofileform','user')
class ProfileFormTestCase(TestCase):
    """Unit tests of the update user details form."""

    fixtures = ['BookClub/tests/fixtures/default_users.json']

    def setUp(self):
        self.form_input = {
            'username': 'johndoe2',
            'email': 'johndoe2@example.org',
            'public_bio': 'My bio',
        }

    def test_form_has_necessary_fields(self):
        form = EditProfileForm()
        self.assertIn('username', form.fields)
        self.assertIn('email', form.fields)
        email_field = form.fields['email']
        self.assertTrue(isinstance(email_field, forms.EmailField))
        self.assertIn('public_bio', form.fields)

    def test_valid_user_form(self):
        form = EditProfileForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_uses_model_validation(self):
        self.form_input['username'] = 'badusername!'
        form = EditProfileForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_must_save_correctly(self):
        user = User.objects.get(username='johndoe')
        form = EditProfileForm(instance=user, data=self.form_input)
        before_count = User.objects.count()
        form.save()
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(user.username, 'johndoe2')
        self.assertEqual(user.email, 'johndoe2@example.org')
        self.assertEqual(user.public_bio, 'My bio')
