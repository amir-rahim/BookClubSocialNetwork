from django.db import models
from django.urls import reverse
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.validators import RegexValidator

from BookClub.models.user import User
from BookClub.models import *
from BookClub.models.club_membership import ClubMembership


class Club(models.Model):
    name = models.CharField(unique=True, max_length=100, blank=False)
    url_name = models.CharField(
            unique=True,
            max_length=100,
            blank=False,
            validators=[
            RegexValidator(
                regex='^[a-zA-Z0-9_]+$',
                message='Can contain A-Z, a-z and 0-9 and underscores characters only.',
                code='invalid_url_name'
            )
        ])
    description = models.CharField(max_length=250, blank=False)
    tagline = models.CharField(max_length=120, blank=True)
    rules = models.CharField(max_length=200, blank=True)
    is_private = models.BooleanField(default=False, blank=False, null=False)
    created_on = models.DateField(auto_now_add=True)

    def get_absolute_url(self):
        return reverse('club_dashboard', kwargs = {'club_url_name': self.url_name})

    def __str__(self):
        return self.name

    def get_club_owner(self):
        return ClubMembership.objects.get(club=self, membership=ClubMembership.UserRoles.OWNER).user

    def get_number_of_members(self):
        return ClubMembership.objects.filter(club=self, membership__gte=ClubMembership.UserRoles.MEMBER).count()

    def is_member(self, user):
        return ClubMembership.objects.filter(club=self, user=user).exists()

    # Has unimplemented dependencies
    def get_number_of_meetings(self):
        pass

    # Has unimplemented dependencies
    def get_number_of_posts(self):
        pass

    # Has unimplemented dependencies
    def get_review_score(self):
        pass

    def get_my_clubs(self):
        try:
            club_ids = ClubMembership.objects.filter(self=self).values_list('Club', flat=True)
            clubs = Club.objects.filter(id__in=club_ids)
        except ObjectDoesNotExist:
            return None
        return clubs

    def get_users(self, search_role):
        """Get all the users from the given club with the given authorization."""

        filterBy = (ClubMembership.objects
                    .filter(club=self)
                    .filter(membership=search_role)
                    .values_list('user__id', flat=True))
        return User.objects.filter(id__in=filterBy)

    def get_members(self):
        """Get all the members from the given club."""

        return self.get_users(ClubMembership.UserRoles.MEMBER)

    def get_moderators(self):
        """Get all the officers from the given club."""

        return self.get_users(ClubMembership.UserRoles.MODERATOR)

    def get_owner(self):
        """Get all the owner from the given club."""

        return self.get_users(ClubMembership.UserRoles.OWNER)
