from urllib import request
from django.test import RequestFactory,TestCase
from BookClub.views import delete_club

class DeleteClubTest(TestCase):

    fixtures = ['default_club_members.json','default_club_owners.json','default_clubs.json','default_memberships.json','BookClub\tests\fixtures\default_users.json']
    def setUp():
        pass

    def test(self):
        request = RequestFactory().get('delete_club/')
        view = delete_club()
        view.setUp(request)

