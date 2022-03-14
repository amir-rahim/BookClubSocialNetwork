from datetime import date

from django.test import TestCase, tag

from BookClub.forms.club import ClubForm
from BookClub.models.club import Club


@tag('forms', 'club')
class ClubFormTestCase(TestCase):
    """Unit tests for Club Form"""

    def setUp(self):
        self.form_input = {
            'name': 'Johnathan\'s Club',
            'club_url_name': 'Johnathans_Club',
            'description': 'This is a very cool club that is owned by a certain Johnathan. Reading certain books...',
            'tagline': 'Welcome to Johnathan\'s club! We read the best books!!!',
            'rules': 'Don\'t be annoying',
            'is_private': False,
            # field created_on is omitted because the model automatically adds the date on save
        }

    def test_valid_club_form(self):
        form = ClubForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_has_necessary_fields(self):
        form = ClubForm()
        self.assertIn('name', form.fields)
        self.assertIn('description', form.fields)
        self.assertIn('tagline', form.fields)
        self.assertIn('rules', form.fields)
        self.assertIn('is_private', form.fields)
        self.assertNotIn('created_on', form.fields)

    def test_form_uses_model_validation(self):
        self.form_input['description'] = 'x' * 251
        form = ClubForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_must_save_correctly(self):
        form = ClubForm(data=self.form_input)
        before_count = Club.objects.count()
        saving_date = date.today()
        form.save()
        after_count = Club.objects.count()
        self.assertEqual(after_count, before_count + 1)
        club = Club.objects.get(name=self.form_input['name'])
        self.assertEqual(club.name, self.form_input['name'])
        self.assertEqual(club.club_url_name, self.form_input['club_url_name'])
        self.assertEqual(club.description, self.form_input['description'])
        self.assertEqual(club.tagline, self.form_input['tagline'])
        self.assertEqual(club.rules, self.form_input['rules'])
        self.assertEqual(club.is_private, self.form_input['is_private'])
        self.assertEqual(club.created_on, saving_date)
