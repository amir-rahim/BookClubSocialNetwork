from datetime import date
from django.forms import PasswordInput

from django.test import TestCase, tag
from django.urls import reverse

from BookClub.models.user import User
from BookClub.models.club import Club
from BookClub.models.club_membership import ClubMembership
from django.contrib.messages import get_messages

from BookClub.tests.helpers import reverse_with_next

@tag('current')
class EditClubViewTestCase(TestCase):
    fixtures = [
        "BookClub/tests/fixtures/default_users.json",
        "BookClub/tests/fixtures/default_clubs.json",
        "BookClub/tests/fixtures/default_club_owners.json",
        "BookClub/tests/fixtures/edit_club_rank_required_helper_fixtures.json"
    ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.user = User.objects.get(username='johndoe')
        self.club = Club.objects.get(pk=1)
        self.url = reverse('edit_club', kwargs = {'url_name': self.club.url_name})
        self.data = {
            'name': 'A test Club',
            'description': 'This is a very cool club that is owned by a certain Johnathan. Reading certain books...',
            'tagline': 'Welcome to Johnathan\'s club! We read the best books!!!',
            'rules': 'Don\'t be annoying',
            'is_private': False,
            'created_on': self.club.created_on,
        }
    def test_edit_club_url(self):
        self.assertEqual(self.url, '/edit_club/'+self.club.url_name+'/')


    def test_post_edit_club_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.post(self.url, self.data, follow=True)
        self.assertRedirects(response, redirect_url,
            status_code=302, target_status_code=200, fetch_redirect_response=True
        )
        self.assertTemplateUsed(response, 'login.html')

    def test_get_edit_club_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url,
            status_code=302, target_status_code=200, fetch_redirect_response=True
        )
        self.assertTemplateUsed(response, 'login.html')

    def test_edit_create_club_logged_in_correct_rank(self):
        self.client.login(username=self.user.username, password='Password123')
        session = self.client.session
        session['club_id'] = self.club.id
        session.save()
        response = self.client.get(self.url)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_club.html')
        self.assertEqual(len(messages), 0)
        
    def test_edit_club_logged_in_not_in_club(self):
        self.client.login(username='janedoe', password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)
        self.assertTemplateNotUsed(response, 'edit_club.html')

    def test_edit_club_logged_in_member_rank(self):
        user = User.objects.get(pk=3)
        self.client.login(username=user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)
        self.assertTemplateNotUsed(response, 'edit_club.html')
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        
    def test_edit_club_logged_in_moderator_rank(self):
        user = User.objects.get(pk=5)
        self.client.login(username=user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)
        self.assertTemplateNotUsed(response, 'edit_club.html')
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        
    def test_edit_club_post_valid_data(self):
        self.client.login(username=self.user.username, password='Password123')
        self.created_on_pre_test = self.club.created_on
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, 302)
        self.club = Club.objects.get(pk=1)
        self.assertEqual(self.club.name, self.data['name'])
        self.assertEqual(self.club.description, self.data['description'])
        self.assertEqual(self.club.tagline, self.data['tagline'])
        self.assertEqual(self.club.rules, self.data['rules'])
        self.assertEqual(self.club.created_on, self.created_on_pre_test)

    def test_edit_club_post_invalid_data(self):
        self.data['name'] = ""
        self.client.login(username=self.user.username, password='Password123')
        self.created_on_pre_test = self.club.created_on
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, 200)
        self.club = Club.objects.get(pk=1)
        self.assertNotEqual(self.club.name, self.data['name'])
        self.assertEqual(self.club.description, self.data['description'])
        self.assertEqual(self.club.tagline, self.data['tagline'])
        self.assertEqual(self.club.rules, self.data['rules'])
        self.assertEqual(self.club.created_on, self.created_on_pre_test)