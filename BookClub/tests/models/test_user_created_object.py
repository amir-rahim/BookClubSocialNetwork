
from django.forms import ValidationError
from django.test import TestCase, tag
from BookClub.models import ForumPost
from BookClub.models.abstract_user_objects import UserCreatedObject
        
@tag('usercreated')        
class UserCreatedObjectTestCase(TestCase):
    fixtures = [
        'BookClub/tests/fixtures/default_user_created_objects.json', 
        'BookClub/tests/fixtures/default_users.json'
        ]
    def setUp(self):
        self.usercreobj = ForumPost.objects.get(pk =1)
        
    def assertValid(self):
        try:
            self.usercreobj.full_clean()
        except(ValidationError):
            self.fail('Test user created object should be valid')

    def assertInvalid(self):
        with self.assertRaises(ValidationError):
            self.usercreobj.full_clean()

    def test_valid_usercreatedobject(self):
        self.assertValid()
        
    def test_forum_subclasses_user_created_object(self):
        assert issubclass(ForumPost, UserCreatedObject)
    
    def test_creator_cannot_be_blank(self):
        self.usercreobj.creator = None
        self.assertInvalid()