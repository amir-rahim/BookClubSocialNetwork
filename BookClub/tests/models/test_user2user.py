

from numbers import Integral
from django.db import IntegrityError
from django.forms import ValidationError
from django.test import TestCase, tag
from BookClub.models.user import User
from BookClub.models.user2user import UserToUserRelationship as U2U
@tag('U2U','models')
class UserToUserTestCase(TestCase):
    
    fixtures = ['BookClub/tests/fixtures/default_users.json',
                'BookClub/tests/fixtures/default_relationships.json'
                ]
    
    def setUp(self):
        self.user1 = User.objects.get(pk=1)
        self.user2 = User.objects.get(pk=2)
        self.rel1 = U2U.objects.get(pk=1)

    def _is_valid(self, relationship):
        try:
            relationship.full_clean()
        except ValidationError:
            self.fail('Test relationship should be valid')
            
    def _is_invalid(self, relationship):
        with self.assertRaises((ValidationError, IntegrityError)):
            relationship.full_clean()
            relationship.save()
            
            
            
    def _save_relationship(self, user1, user2, type):
        relationship = U2U.objects.create(
            source_user=self.user1,
            target_user = self.user2,
            relationship_type=type
        )
        return relationship
        
    def test_create_relationship(self):
        self.rel1.delete()
        relationship = self._save_relationship(
            self.user1, self.user2, U2U.UToURelationshipTypes.MUTUAL_FOLLOWING)
        self._is_valid(relationship)
        
    def test_unique_constraint(self):
        with self.assertRaises(IntegrityError):
            relationship = self._save_relationship(
                self.user1, self.user2, U2U.UToURelationshipTypes.MUTUAL_FOLLOWING)
            
    def test_source_user_cannot_be_null(self):
        self.rel1.source_user = None
        self._is_invalid(self.rel1)
        
    def test_target_user_cannot_be_null(self):
        self.rel1.target_user = None
        self._is_invalid(self.rel1)
        
    def test_target_created_on_cannot_be_null(self):
        self.rel1.created_on = None
        self._is_invalid(self.rel1)
        
    def test_relationship_type_cannot_be_null(self):
        self.rel1.relationship_type = None
        self._is_invalid(self.rel1)
        
    def test_relationship_type_must_be_a_choice(self):
        self.rel1.relationship_type = "mutuals"
        self._is_invalid(self.rel1)
