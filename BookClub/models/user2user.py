from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import UniqueConstraint

class UserToUserRelationship(models.Model):
    class UToURelationshipTypes(models.IntegerChoices):
        FOLLOWING = 1
    class Meta:
        constraints = [
            UniqueConstraint(fields=['source_user', 'target_user'], name='unique_relationship')
        ]

    source_user = models.ForeignKey('User', on_delete=models.CASCADE,related_name='user_relationships_source')
    target_user = models.ForeignKey('User', on_delete=models.CASCADE,related_name='user_relationships_target')
    relationship_type = models.IntegerField(
        choices=UToURelationshipTypes.choices, blank=False, null=False)
    created_on = models.DateTimeField(auto_now_add=True, blank=False, null=False)
