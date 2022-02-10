from django.shortcuts import redirect
from django.urls import reverse
from django.test import TestCase, override_settings
from django.views.generic import View
from BookClub.models.club_membership import ClubMembership
from BookClub.models.club import Club
from BookClub.models.user import User
from BookClub.helpers import RankRequiredMixin
from BookClub.tests.helpers import LogInTester

class TestView(RankRequiredMixin, View):
        
    requiredRanking = ClubMembership.UserRoles.OWNER
    requiredClub = 1
    def get(self, request, *args, **kwargs):
        return redirect('login')
        
@override_settings(ROOT_URLCONF='BookClub.tests.helpers_tests.helpers_urls')
class RankRequiredTextCase(TestCase, LogInTester):
    
    
    fixtures = [
        'BookClub/tests/fixtures/default_users.json',
        'BookClub/tests/fixtures/default_clubs.json',
        'BookClub/tests/fixtures/default_club_owners.json',
        'BookClub/tests/fixtures/edit_club_rank_required_helper_fixtures.json'
    ]
        
    def setUp(self):
        self.url = reverse('test_rank_required')
        self.user = User.objects.get(pk = 1)
        self.club = Club.objects.get(pk=1)
        return super().setUp()
        
    def test_user_has_required_rank_and_club(self):
        self.client.login(username='johndoe', password='Password123')
        self.assertEqual(self._is_logged_in(), True)
        session = self.client.session
        session['club_id'] = 1
        session.save()
        response = self.client.get(self.url)
        self.assertEqual(response.url, "/login/")
        
    def test_user_has_required_rank_but_not_club(self):
        self.client.login(username='janedoe', password='Password123')
        self.assertEqual(self._is_logged_in(), True)
        response = self.client.get(self.url)
        self.assertEqual(response.url, reverse('home'))
        
    def test_user_does_not_have_required_rank_but_is_in_club(self):
        self.client.login(username='joedoe',password='Password123')
        self.assertEqual(self._is_logged_in(), True)
        session = self.client.session
        session['club_id'] = 1
        session.save()
        response = self.client.get(self.url)
        self.assertEqual(response.url, reverse('home'))
        
    def test_user_does_not_have_required_rank_and_is_not_in_club(self):
        self.client.login(username='jeffbezdoe',password='Password123')
        self.assertEqual(self._is_logged_in(), True)
        response = self.client.get(self.url)
        self.assertEqual(response.url, reverse('home'))
        