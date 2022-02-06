
from django.template import Context
from BookClub.tests.helpers import LogInTester
from BookClub.helpers import get_club_id
from django.test.client import RequestFactory        
from django.urls import reverse
from django.test import TestCase

class GetClubIdTestCase(TestCase, LogInTester):
    
    fixtures = [
        'BookClub/tests/fixtures/default_users.json',
        'BookClub/tests/fixtures/default_clubs.json',
        'BookClub/tests/fixtures/default_club_owners.json',
    ]
    
    def setUp(self):
        self.rf = RequestFactory()
        self.url = reverse('home')
        
    def test_confirm_url(self):
        self.assertEqual(self.url, '/')
        
    def test_user_has_no_club(self):
        request = self.rf.get('/')
        self.assertEqual(get_club_id(request), -1)
        
    def test_user_has_club(self):
        request = self.rf.get('/')
        request.session = self.client.session
        request.session['club'] = 1
        self.assertEqual(get_club_id(request),1)
        
    def test_user_has_id_but_club_does_not_exist(self):
        request = self.rf.get('/')
        request.session = self.client.session
        request.session['club'] = 10000
        self.assertEqual(get_club_id(request),-1)