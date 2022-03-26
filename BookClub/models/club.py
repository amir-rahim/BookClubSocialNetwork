import re

from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import RegexValidator
from django.db import IntegrityError, models
from django.urls import reverse

from BookClub.models import ClubMembership, User


class Club(models.Model):
    
    class Meta:
        ordering = ['name']
    name = models.CharField(unique=True, max_length=100, blank=False)
    club_url_name = models.CharField(
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

    def clean(self):
        url = self.convertNameToUrl(self.name)
        self.club_url_name = url
        super().clean()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs);
        forum_model = apps.get_model('BookClub', 'forum')
        associated_with = forum_model.objects.get_or_create(title=self.club_url_name + " forum", associated_with = self)

    def get_absolute_url(self):
        return reverse('club_dashboard', kwargs = {'club_url_name': self.club_url_name})

    def __str__(self):
        return self.name

    def get_club_owner(self):
        return ClubMembership.objects.get(club=self, membership=ClubMembership.UserRoles.OWNER).user

    def get_number_of_members(self):
        return ClubMembership.objects.filter(club=self, membership__gte=ClubMembership.UserRoles.MEMBER).count()

    def is_applicant(self, user):
        return ClubMembership.objects.filter(club=self, user=user, membership__gte=ClubMembership.UserRoles.APPLICANT).exists()

    def is_member(self, user):
        return ClubMembership.objects.filter(club=self, user=user, membership__gte=ClubMembership.UserRoles.MEMBER).exists()

    def is_moderator(self, user):
        return ClubMembership.objects.filter(club=self, user=user, membership__gte=ClubMembership.UserRoles.MODERATOR).exists()

    def is_owner(self, user):
        return ClubMembership.objects.filter(club=self, user=user, membership__gte=ClubMembership.UserRoles.OWNER).exists()

    def convertNameToUrl(self, name):
        updated = re.sub(" +", "_", name)
        updated = re.sub("[^0-9a-zA-Z_]+", "", updated)
        return updated

    def get_number_of_meetings(self):
        return self.meeting_set.all().count()

    def get_number_of_posts(self):
        return self.forum.get_posts().count()

    # Has unimplemented dependencies
    def get_review_score(self):
        pass

    def get_users(self, search_role):
        """Get all the users from the given club with the given authorization."""

        filter_by = (ClubMembership.objects
                    .filter(club=self)
                    .filter(membership=search_role)
                    .values_list('user__id', flat=True))
        return User.objects.filter(id__in=filter_by)

    def get_applicants(self):
        """Get all the applicants from the  given club."""

        return self.get_users(ClubMembership.UserRoles.APPLICANT)

    def get_members(self):
        """Get all the members from the given club."""

        return self.get_users(ClubMembership.UserRoles.MEMBER)

    def get_moderators(self):
        """Get all the officers from the given club."""

        return self.get_users(ClubMembership.UserRoles.MODERATOR)

    def get_owner(self):
        """Get all the owner from the given club."""

        return self.get_users(ClubMembership.UserRoles.OWNER)

    def add_user(self, user, rank):
        try:
            ClubMembership.objects.create(
                user=user,
                club=self,
                membership=rank,
            )
        except IntegrityError:
            pass

    def add_member(self, user):
        self.add_user(user, ClubMembership.UserRoles.MEMBER)

    def add_moderator(self, user):
        self.add_user(user, ClubMembership.UserRoles.MODERATOR)

    def add_owner(self, user):
        if not ClubMembership.objects.filter(club=self, membership=ClubMembership.UserRoles.OWNER).exists():
            self.add_user(user, ClubMembership.UserRoles.OWNER)
        else:
            # print("Owner already set")
            pass

    def add_applicant(self, user):
        self.add_user(user, ClubMembership.UserRoles.APPLICANT)

    def remove_from_club(self, user):
        ClubMembership.objects.filter(user=user, club=self).delete()
