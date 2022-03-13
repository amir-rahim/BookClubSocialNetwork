"""Test the Create Club Poll view."""
from datetime import datetime, timedelta

import pytz
from django.contrib import messages
from django.contrib.messages import get_messages
from django.test import TestCase, tag
from django.urls import reverse

from BookClub.forms import PollForm
from BookClub.models import Club, ClubMembership, Poll, Option, Book
from BookClub.tests.helpers import reverse_with_next


@tag('poll', 'create_poll')
class CreateClubPollViewTestCase(TestCase):
    """Test the Create Club Poll view."""

    fixtures = [
        "BookClub/tests/fixtures/default_users.json",
        "BookClub/tests/fixtures/default_clubs.json",
        "BookClub/tests/fixtures/default_books.json",
        "BookClub/tests/fixtures/default_club_members.json",
    ]

    def setUp(self):
        self.club = Club.objects.get(pk=1)
        self.member = ClubMembership.objects.filter(club=self.club, membership=ClubMembership.UserRoles.MEMBER)[0].user
        self.moderator = ClubMembership.objects.filter(club=self.club, membership=ClubMembership.UserRoles.MODERATOR)[
            0].user
        self.owner = ClubMembership.objects.filter(club=self.club, membership=ClubMembership.UserRoles.OWNER)[0].user

        self.private_club = Club.objects.get(pk=3)
        self.url_private_club = reverse('create_club_poll', kwargs={'club_url_name': self.private_club.club_url_name})

        self.url = reverse('create_club_poll', kwargs={'club_url_name': self.club.club_url_name})

        self.harry_potter_book = Book.objects.get(pk=4)
        self.selfhelp_book = Book.objects.get(pk=2)
        self.deadline = pytz.utc.localize(datetime.now() + timedelta(days=1))

        self.data = {
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

            'option_5_text': 'Just for fun',
            'option_5_isbn': '',
        }

    def test_create_meeting_url(self):
        self.assertEqual(self.url, f'/club/{self.club.club_url_name}/polls/create/')

    def test_post_create_poll_redirects_when_not_logged_in(self):
        polls_count_before = Poll.objects.count()
        options_count_before = Option.objects.count()
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.post(self.url, self.data, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200,
                             fetch_redirect_response=True)
        self.assertTemplateUsed(response, 'login.html')
        polls_count_after = Poll.objects.count()
        options_count_after = Option.objects.count()
        self.assertEqual(polls_count_after, polls_count_before)
        self.assertEqual(options_count_after, options_count_before)

    def test_get_create_poll_redirects_when_not_logged_in(self):
        polls_count_before = Poll.objects.count()
        options_count_before = Option.objects.count()
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200,
                             fetch_redirect_response=True)
        self.assertTemplateUsed(response, 'login.html')
        polls_count_after = Poll.objects.count()
        options_count_after = Option.objects.count()
        self.assertEqual(polls_count_after, polls_count_before)
        self.assertEqual(options_count_after, options_count_before)

    '''Tests for users which can see the create meeting form'''

    def test_owner_can_see_create_poll_template(self):
        self.client.login(username=self.owner.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_club_poll.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, PollForm))
        self.assertFalse(form.is_bound)

    '''Tests for users which cannot see the create meeting form'''

    def test_member_cannot_see_create_poll_template(self):
        self.client.login(username=self.member.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)
        # response_message = self.client.get(reverse('club_dashboard', kwargs={'club_url_name': self.club.club_url_name}))
        # messages_list = list(response_message.context['messages'])
        # messages_list = list(get_messages(response.wsgi_request))
        # self.assertEqual(len(messages_list), 1)
        # self.assertEqual(messages_list[0].level, messages.ERROR)

    '''Tests for users successfully creating a meeting'''

    def test_moderator_create_poll(self):
        self.client.login(username=self.moderator.username, password='Password123')

        polls_before_count = Poll.objects.count()
        options_before_count = Option.objects.count()
        saving_datetime = pytz.utc.localize(datetime.now())
        response = self.client.post(self.url, self.data, follow=True)
        redirect_url = reverse('club_dashboard', kwargs={'club_url_name': self.club.club_url_name})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200,
                             fetch_redirect_response=True)

        messages_list = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.SUCCESS)
        polls_after_count = Poll.objects.count()
        options_after_count = Option.objects.count()

        self.assertEqual(polls_after_count, polls_before_count + 1)

        poll = Poll.objects.get(title=self.data['poll_title'])
        self.assertTemplateUsed(response, 'club_dashboard.html')
        self.assertEqual(poll.title, self.data['poll_title'])
        self.assertEqual(poll.deadline, self.data['deadline'])
        self.assertEqual(poll.active, saving_datetime < poll.deadline)
        self.assertEqual(poll.club, self.club)
        self.assertEqual(poll.created_on.date(), saving_datetime.date())

        self.assertEqual(options_after_count, options_before_count + 4)

        options = list(Option.objects.filter(poll=poll))
        self.assertEqual(len(options), 4)

        for option in options:
            self.assertEqual(option.voted_by.count(), 0)

        self.assertEqual(options[0].text, self.data['option_1_text'])
        self.assertEqual(options[0].book, None)

        self.assertEqual(options[1].text, self.data['option_2_text'])
        self.assertEqual(options[1].book, self.harry_potter_book)

        self.assertEqual(options[2].text, self.data['option_3_text'])
        self.assertEqual(options[2].book, self.selfhelp_book)

        self.assertEqual(options[3].text, self.data['option_5_text'])
        self.assertEqual(options[3].book, None)

    '''Tests for users with permission unsuccessfully creating a meeting'''

    def test_owner_create_wrong_poll(self):
        self.client.login(username=self.owner.username, password='Password123')
        self.data['option_2_isbn'] = '8732648762384'
        polls_before_count = Poll.objects.count()
        options_before_count = Option.objects.count()
        response = self.client.post(self.url, self.data)
        polls_after_count = Poll.objects.count()
        options_after_count = Option.objects.count()
        self.assertEqual(polls_after_count, polls_before_count)
        self.assertEqual(options_after_count, options_before_count)
        messages_list = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_club_poll.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, PollForm))
        self.assertTrue(form.is_bound)

    '''Tests for users not being able to creating a meeting'''

    def test_member_create_poll(self):
        self.client.login(username=self.member.username, password='Password123')
        polls_before_count = Poll.objects.count()
        options_before_count = Option.objects.count()
        response = self.client.post(self.url, self.data, follow=True)
        self.assertEqual(response.status_code, 403)
        # messages_list = list(get_messages(response.wsgi_request))
        # self.assertEqual(len(messages_list), 1)
        # self.assertEqual(messages_list[0].level, messages.ERROR)
        polls_after_count = Poll.objects.count()
        options_after_count = Option.objects.count()
        self.assertEqual(polls_after_count, polls_before_count)

    '''Tests for users creating meetings for another club'''

    def test_moderator_of_club_cannot_create_meetings_for_another_private_club(self):
        self.client.login(username=self.moderator.username, password='Password123')
        response = self.client.post(self.url_private_club, self.data, follow=True)
        self.assertEqual(response.status_code, 403)

    def test_member_of_club_cannot_create_meetings_for_another_private_club(self):
        self.client.login(username=self.member.username, password='Password123')
        response = self.client.post(self.url_private_club, self.data, follow=True)
        self.assertEqual(response.status_code, 403)

    '''Tests for users creating meetings for invalid club'''

    def test_owner_cannot_create_meeting_for_invalid_club(self):
        self.client.login(username=self.owner.username, password='Password123')
        polls_before_count = Poll.objects.count()
        options_before_count = Option.objects.count()
        response = self.client.post(reverse('create_club_poll', kwargs={'club_url_name': 'wrong'}), self.data,
                                    follow=True)
        # messages_list = list(get_messages(response.wsgi_request))
        # self.assertEqual(len(messages_list), 1)
        # self.assertEqual(messages_list[0].level, messages.ERROR)
        self.assertEqual(response.status_code, 404)
        polls_after_count = Poll.objects.count()
        options_after_count = Option.objects.count()
        self.assertEqual(polls_after_count, polls_before_count)
