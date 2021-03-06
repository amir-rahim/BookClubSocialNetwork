"""Club Membership model."""
from django.core.exceptions import ValidationError
from django.db import models

from BookClub.models.user import User


class ClubMembership(models.Model):
    """Club Membership model to created a relation between the User and a Club.
    
    Attributes:
        user: The User in the relationship.
        club: The Club the User is in.
        membership: The UserRole to specify the User's role in the Club.
        joined_on: The Date the User joined the Club.
    """
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'club'], name='unique_member')
        ]

    class UserRoles(models.IntegerChoices):
        """User Role model to specify the User role in the Club."""
        APPLICANT = -1
        MEMBER = 0
        MODERATOR = 1
        OWNER = 2

    user = models.ForeignKey(User, blank=False, null=False, on_delete=models.CASCADE)
    club = models.ForeignKey('Club', blank=False, null=False, on_delete=models.CASCADE)
    membership = models.IntegerField(choices=UserRoles.choices, blank=False, default=UserRoles.APPLICANT)
    joined_on = models.DateField(auto_now_add=True)

    def clean(self):
        super().clean()
        if self.membership == ClubMembership.UserRoles.OWNER:
            if len(ClubMembership.objects.filter(
                club = self.club,
                membership = ClubMembership.UserRoles.OWNER
            ).exclude(user = self.user)) > 0:
                raise ValidationError(message = 'A club can only have 1 owner')

