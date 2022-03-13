from datetime import datetime, timedelta

import pytz
from django.test import TestCase, tag

from BookClub.forms import PollForm, ISBNField
from BookClub.models import Poll, Option, Club, Book


@tag('forms', 'poll', 'option')
class PollFormTestcase(TestCase):
    fixtures = [
        'BookClub/tests/fixtures/default_books.json',
        'BookClub/tests/fixtures/default_clubs.json'
    ]

    def setUp(self):
        self.club = Club.objects.get(pk=1)
        self.harry_potter_book = Book.objects.get(pk=4)
        self.selfhelp_book = Book.objects.get(pk=2)
        self.deadline = pytz.utc.localize(datetime.now() + timedelta(days=1))

        self.form_input = {
            'poll_title': 'Vote on your favourite option',
            'deadline': self.deadline,
            'option_1_text': 'We don\'t need a book',
            'option_1_isbn': '',

            'option_2_text': 'We need a Harry Potter book!',
            'option_2_isbn': self.harry_potter_book.ISBN,

            'option_3_text': 'We need a self-help book!',
            'option_3_isbn': self.selfhelp_book.ISBN,

            'option_4_text': '',
            'option_4_isbn': '',

            'option_5_text': '',
            'option_5_isbn': '',
        }

    def test_form_has_necessary_fields(self):
        form = PollForm()
        self.assertIn('poll_title', form.fields)
        self.assertIn('deadline', form.fields)

        for i in range(1, 6):
            self.assertIn('option_' + str(i) + '_text', form.fields)
            self.assertIn('option_' + str(i) + '_isbn', form.fields)
            self.assertTrue(isinstance(form.fields['option_' + str(i) + '_isbn'], ISBNField))

    def test_form_uses_custom_validation(self):
        self.form_input['option_3_isbn'] = ('1' * 9) + 'A'
        form = PollForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_valid_poll_form(self):
        form = PollForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_valid_poll_form_saves_with_provided_club_correctly(self):
        form = PollForm(data=self.form_input)

        poll_before_count = Poll.objects.count()
        options_before_count = Option.objects.count()
        saving_datetime = datetime.now()

        (poll, options) = form.save(club=self.club)

        poll_after_count = Poll.objects.count()
        options_after_count = Option.objects.count()
        self.assertEqual(poll_after_count, poll_before_count + 1)
        self.assertEqual(options_after_count, options_before_count + 3)

        self.assertEqual(poll.title, self.form_input['poll_title'])
        self.assertEqual(poll.deadline, self.form_input['deadline'])
        self.assertEqual(poll.active, pytz.utc.localize(saving_datetime) < poll.deadline)
        self.assertEqual(poll.club, self.club)
        self.assertEqual(poll.created_on.date(), saving_datetime.date())

        self.assertEqual(len(options), 3)

        for option in options:
            self.assertEqual(option.poll, poll)
            self.assertEqual(option.voted_by.count(), 0)

        self.assertEqual(options[0].text, self.form_input['option_1_text'])
        self.assertEqual(options[0].book, None)

        self.assertEqual(options[1].text, self.form_input['option_2_text'])
        self.assertEqual(options[1].book, self.harry_potter_book)

        self.assertEqual(options[2].text, self.form_input['option_3_text'])
        self.assertEqual(options[2].book, self.selfhelp_book)
