from datetime import date
from django.forms import PasswordInput

from django.test import TestCase, tag
from django.urls import reverse

from BookClub.models.user import User
from BookClub.models.club import Club
from BookClub.models.club_membership import ClubMembership
from django.contrib.messages import get_messages

from BookClub.tests.helpers import reverse_with_next
"""
    Testing for edit_club
    Carried out by Jack and Rav
"""
@tag('editclub','club')
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
        self.url = reverse('edit_club', kwargs = {'club_url_name': self.club.club_url_name})
        self.data = {
            'name': "Johnathan Club",
            'description': 'This is a very cool club that is owned by a certain Johnathan. Reading certain books...',
            'tagline': 'Welcome to Johnathan\'s club! We read the best books!!!',
            'rules': 'Don\'t be annoying',
            'is_private': False,
            'created_on': self.club.created_on,
        }
        
    def test_edit_club_url(self):
        self.assertEqual(self.url, '/club/'+self.club.club_url_name+'/edit/')


    def test_post_edit_club_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.post(self.url, self.data, follow=True)
        self.assertRedirects(response, redirect_url,
            status_code=302, target_status_code=200, fetch_redirect_response=True
        )
        self.assertTemplateUsed(response, 'login.html')

    def test_get_edit_club_redirects_when_not_logged_in_invalid_club(self):
        url = reverse('edit_club', kwargs= {'club_url_name' : 'fakeclub'})
        redirect_url = reverse_with_next('login', url)
        response = self.client.get(url, follow=True)
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
        self.assertEqual(response.status_code, 302)
        self.assertTemplateNotUsed(response, 'edit_club.html')

    def test_edit_club_logged_in_member_rank(self):
        user = User.objects.get(pk=3)
        self.client.login(username=user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertTemplateNotUsed(response, 'edit_club.html')
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)

    def test_edit_club_logged_in_moderator_rank(self):
        user = User.objects.get(pk=5)
        self.client.login(username=user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertTemplateNotUsed(response, 'edit_club.html')
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)

    def test_edit_club_post_valid_data_name_change(self):
        self.client.login(username=self.user.username, password='Password123')
        self.created_on_pre_test = self.club.created_on
        self.data['name'] = 'Test club'
        response = self.client.post(self.url, self.data)
       
        self.club = Club.objects.get(pk=1)
        responseUrl = reverse('club_dashboard', kwargs = {'club_url_name' : self.club.club_url_name})
        self.assertRedirects(response, expected_url=responseUrl, status_code=302, target_status_code=200)
        self.assertEqual(self.club.name, self.data['name'])
        self.assertEqual(self.club.description, self.data['description'])
        self.assertEqual(self.club.tagline, self.data['tagline'])
        self.assertEqual(self.club.rules, self.data['rules'])
        self.assertEqual(self.club.is_private, self.data['is_private'])
        self.assertEqual(self.club.created_on, self.created_on_pre_test)
        self.assertEqual(response.status_code, 302)
    
    def test_edit_club_post_valid_data_description_change(self):
        self.client.login(username=self.user.username, password='Password123')
        self.created_on_pre_test = self.club.created_on
        self.data['description'] = "test description"
        response = self.client.post(self.url, self.data)
        
        self.club = Club.objects.get(pk=1)
        responseUrl = reverse('club_dashboard', kwargs = {'club_url_name' : self.club.club_url_name})
        self.assertRedirects(response, expected_url=responseUrl, status_code=302, target_status_code=200)
        self.assertEqual(self.club.name, self.data['name'])
        self.assertEqual(self.club.description, self.data['description'])
        self.assertEqual(self.club.tagline, self.data['tagline'])
        self.assertEqual(self.club.rules, self.data['rules'])
        self.assertEqual(self.club.is_private, self.data['is_private'])
        self.assertEqual(self.club.created_on, self.created_on_pre_test)
        self.assertEqual(response.status_code, 302)
        
    def test_edit_club_post_valid_data_rules_change(self):
        self.client.login(username=self.user.username, password='Password123')
        self.created_on_pre_test = self.club.created_on
        self.data['rules'] = "test rules"
        response = self.client.post(self.url, self.data)
        self.club = Club.objects.get(pk=1)
        responseUrl = reverse('club_dashboard', kwargs = {'club_url_name' : self.club.club_url_name})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, expected_url=responseUrl, status_code=302, target_status_code=200)
        self.assertEqual(self.club.name, self.data['name'])
        self.assertEqual(self.club.description, self.data['description'])
        self.assertEqual(self.club.tagline, self.data['tagline'])
        self.assertEqual(self.club.rules, self.data['rules'])
        self.assertEqual(self.club.is_private, self.data['is_private'])
        self.assertEqual(self.club.created_on, self.created_on_pre_test)


            
    def test_edit_club_post_valid_data_tagline_change(self):
        self.client.login(username=self.user.username, password='Password123')
        self.created_on_pre_test = self.club.created_on
        self.data['tagline'] = "tagline test"
        response = self.client.post(self.url, self.data)
        self.club = Club.objects.get(pk=1)
        responseUrl = reverse('club_dashboard', kwargs = {'club_url_name' : self.club.club_url_name})
        self.assertRedirects(response, expected_url=responseUrl, status_code=302, target_status_code=200)
        self.assertEqual(self.club.name, self.data['name'])
        self.assertEqual(self.club.description, self.data['description'])
        self.assertEqual(self.club.tagline, self.data['tagline'])
        self.assertEqual(self.club.rules, self.data['rules'])
        self.assertEqual(self.club.is_private, self.data['is_private'])
        self.assertEqual(self.club.created_on, self.created_on_pre_test)
        self.assertEqual(response.status_code, 302)
        
    def test_edit_club_post_valid_data_is_private_change(self):
        self.client.login(username=self.user.username, password='Password123')
        self.created_on_pre_test = self.club.created_on
        self.data['is_private'] = True
        response = self.client.post(self.url, self.data)
        self.club = Club.objects.get(pk=1)
        responseUrl = reverse('club_dashboard', kwargs = {'club_url_name' : self.club.club_url_name})
        self.assertRedirects(response, expected_url=responseUrl, status_code=302, target_status_code=200)
        self.assertEqual(self.club.name, self.data['name'])
        self.assertEqual(self.club.description, self.data['description'])
        self.assertEqual(self.club.tagline, self.data['tagline'])
        self.assertEqual(self.club.rules, self.data['rules'])
        self.assertEqual(self.club.is_private, self.data['is_private'])
        self.assertEqual(self.club.created_on, self.created_on_pre_test)
        self.assertEqual(response.status_code, 302)
        

    def test_edit_club_post_invalid_data_name(self):
        self.client.login(username=self.user.username, password='Password123')
        self.created_on_pre_test = self.club.created_on
        self.data['name'] = ""
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, 200)
        self.club = Club.objects.get(pk=1)
        self.assertNotEqual(self.club.name, self.data['name'])
        self.assertEqual(self.club.description, self.data['description'])
        self.assertEqual(self.club.tagline, self.data['tagline'])
        self.assertEqual(self.club.rules, self.data['rules'])
        self.assertEqual(self.club.is_private, self.data['is_private'])
        self.assertEqual(self.club.created_on, self.created_on_pre_test)
        
    def test_edit_club_post_invalid_data_description(self):
        self.client.login(username=self.user.username, password='Password123')
        self.created_on_pre_test = self.club.created_on
        self.data['description'] = ""
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, 200)
        self.club = Club.objects.get(pk=1)
        self.assertEqual(self.club.name, self.data['name'])
        self.assertNotEqual(self.club.description, self.data['description'])
        self.assertEqual(self.club.tagline, self.data['tagline'])
        self.assertEqual(self.club.rules, self.data['rules'])
        self.assertEqual(self.club.is_private, self.data['is_private'])
        self.assertEqual(self.club.created_on, self.created_on_pre_test)

        
    
