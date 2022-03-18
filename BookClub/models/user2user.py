from django.core.exceptions import ValidationError
from django.db import models

from BookClub.models.user import User

class User2UserRelationship(models.Model):
    class U2URelationshipTypes(models.IntegerChoices):
        FOLLOWING = '0'
        FOLLOWEE = '1'
        MUTUAL = '2'
        
    class Meta:
        unique_together= [['user1', 'user2']]
        
    user1 = models.ForeignKey('User', on_delete=models.CASCADE)
    user2 = models.ForeignKey('User', on_delete=models.CASCADE)
    relationship_type = models.IntegerField(
        choices=U2URelationshipTypes, blank=False, null=False)
    created_on = models.DateTimeField(auto_now_add=True, blank=False, null=False)
