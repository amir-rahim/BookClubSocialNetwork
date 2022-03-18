


from django.test import TestCase
from BookClub.models.user import User
from BookClub.models.user2user import User2UserRelationship as U2U

class User2UserTestCase(TestCase):
    
    fixtures = ['BookClub/tests/fixtures/default_users.json',
                'BookClub/tests/fixtures/default_relationships.json'
                ]
    
    def setUp(self):
        self.user1 = User.objects.get(pk=1)
        self.user2 = User.objects.get(pk=2)
        self.rel1 = U2U.objects.get(pk=1)

    def _is_valid(self):
        try:
            self.user.full_clean()
        except ValidationError:
            self.fail('Test user should be valid')
