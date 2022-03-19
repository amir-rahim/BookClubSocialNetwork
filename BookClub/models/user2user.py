from django.core.exceptions import ValidationError
from django.db import models

from BookClub.models.user import User

class UserToUserRelationship(models.Model):
    class UToURelationshipTypes(models.IntegerChoices):
        USER1_FOLLOWING = 0
        USER2_FOLLOWING = 1
        MUTUAL_FOLLOWING = 2
        
    class Meta:
        models.UniqueConstraint(
            fields=['source_user', 'target_user'], name='unique_relation')
        
    source_user = models.ForeignKey('User', on_delete=models.CASCADE, related_name="source_user_relationships")
    target_user = models.ForeignKey('User', on_delete=models.CASCADE, related_name="target_user_relationships")
    relationship_type = models.IntegerField(
        choices=UToURelationshipTypes.choices, blank=False, null=False)
    created_on = models.DateTimeField(auto_now_add=True, blank=False, null=False)
