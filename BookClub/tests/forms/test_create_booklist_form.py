from datetime import datetime
import pytz

from django.test import TestCase, tag

from BookClub.forms.booklist_forms import CreateBookListForm
from BookClub.models import BookList, User


@tag('forms', 'booklist')
class BookListFormTestCase(TestCase):
    """Unit tests for Book List Form"""

    fixtures = [
        "BookClub/tests/fixtures/default_users.json",
    ]

    def setUp(self):
        self.user = User.objects.get(username='johndoe')
        self.form_input = {
            'title': 'my new booklist',
            'description': 'All of my favourite books <3'
        }

    def test_valid_create_booklist_form(self):
        form = CreateBookListForm(data = self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_has_necessary_fields(self):
        form = CreateBookListForm()
        self.assertIn('title', form.fields)
        self.assertIn('description', form.fields)

    def test_form_uses_model_validation(self):
        self.form_input['title'] = 'y' * 121
        self.form_input['description'] = 'x' * 241
        form = CreateBookListForm(data = self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_must_save_correctly(self):
        form = CreateBookListForm(data = self.form_input)
        form.instance.creator = self.user
        saving_date = pytz.utc.localize(datetime.today()).date()
        before_count = BookList.objects.count()
        form.save()
        after_count = BookList.objects.count()
        self.assertEqual(after_count, before_count + 1)
        booklist = BookList.objects.get(title = self.form_input['title'])
        self.assertEqual(booklist.title, self.form_input['title'])
        self.assertEqual(booklist.description, self.form_input['description'])
        self.assertEqual(booklist.creator, self.user)
        self.assertEqual(booklist.created_on.date(), saving_date)

    def test_input_boundaries_save_successfully(self):
        self.form_input['title'] = 'y' * 120
        self.form_input['description'] = 'x' * 240
        form = CreateBookListForm(instance = self.user, data = self.form_input)
        self.assertTrue(form.is_valid())
