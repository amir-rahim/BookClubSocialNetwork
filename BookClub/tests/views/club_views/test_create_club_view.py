"""Unit testing of the Create Club view"""
from datetime import date

from django.test import TestCase, tag
from django.urls import reverse

from BookClub.forms.club import ClubForm
from BookClub.models.club import Club
from BookClub.models.club_membership import ClubMembership
from BookClub.models.user import User
from BookClub.tests.helpers import reverse_with_next


@tag('views', 'club', 'create_club')
class CreateClubViewTestcase(TestCase):
    """Testing the Create Club view"""
    fixtures = [
        "BookClub/tests/fixtures/default_users.json",
        "BookClub/tests/fixtures/default_clubs.json",
    ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.user = User.objects.get(username='johndoe')
        self.url = reverse('create_club')
        self.data = {
            'name': 'A test Club',
            'description': 'This is a very cool club that is owned by a certain Johnathan. Reading certain books...',
            'tagline': 'Welcome to Johnathan\'s club! We read the best books!!!',
            'rules': 'Don\'t be annoying',
            'is_private': False,
            # field created_on is omitted because the model automatically adds the date on save
        }

    def test_create_club_url(self):
        self.assertEqual(self.url, '/create/')

    def test_post_create_club_redirects_when_not_logged_in(self):
        club_count_before = Club.objects.count()
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.post(self.url, self.data, follow=True)
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200, fetch_redirect_response=True
                             )
        self.assertTemplateUsed(response, 'authentication/login.html')
        club_count_after = Club.objects.count()
        self.assertEqual(club_count_after, club_count_before)

    def test_get_create_club_redirects_when_not_logged_in(self):
        club_count_before = Club.objects.count()
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200, fetch_redirect_response=True
                             )
        self.assertTemplateUsed(response, 'authentication/login.html')
        club_count_after = Club.objects.count()
        self.assertEqual(club_count_after, club_count_before)

    def test_get_create_club(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'clubs/create_club.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, ClubForm))
        self.assertFalse(form.is_bound)

    def test_unsuccesful_create_club(self):
        self.client.login(username=self.user.username, password='Password123')
        self.data['name'] = Club.objects.get(pk=1).name
        before_count = Club.objects.count()
        response = self.client.post(self.url, self.data)
        after_count = Club.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'clubs/create_club.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, ClubForm))
        self.assertTrue(form.is_bound)

    def test_succesful_create_club(self):
        self.client.login(username=self.user.username, password='Password123')
        before_count = Club.objects.count()
        saving_date = date.today()
        response = self.client.post(self.url, self.data, follow=True)
        club = Club.objects.get(name=self.data['name'])
        after_count = Club.objects.count()
        self.assertEqual(after_count, before_count + 1)
        response_url = reverse('club_dashboard', kwargs={'club_url_name': club.club_url_name})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'clubs/club_dashboard.html')
        self.assertEqual(club.name, self.data['name'])
        self.assertEqual(club.description, self.data['description'])
        self.assertEqual(club.tagline, self.data['tagline'])
        self.assertEqual(club.rules, self.data['rules'])
        self.assertEqual(club.is_private, self.data['is_private'])
        self.assertEqual(club.rules, self.data['rules'])
        self.assertEqual(club.created_on, saving_date)

        club_owner = ClubMembership.objects.get(club=club, membership=ClubMembership.UserRoles.OWNER).user
        self.assertEqual(club_owner, self.user)
