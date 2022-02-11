from django.db import models
from django.urls import reverse
from django.core.exceptions import ValidationError

from BookClub.models.user import User
from BookClub.models.club_membership import ClubMembership

class Club(models.Model):
    name = models.CharField(unique = True, max_length = 100, blank = False)
    description = models.CharField(max_length = 250, blank = False)
    tagline = models.CharField(max_length = 120, blank = True)
    rules = models.CharField(max_length = 200, blank = True)
    is_private = models.BooleanField(default = False, blank = False, null = False)
    created_on = models.DateField(auto_now_add = True)

    # uncomment this method and substitute the path name for view to show club details
    # def get_absolute_url(self):
    #     return reverse('club', kwargs = {'pk': self.pk})

    def __str__(self):
        return self.name

    def get_club_owner(self):
        return ClubMembership.objects.get(club = self, membership = ClubMembership.UserRoles.OWNER).user

    def get_number_of_members(self):
        return ClubMembership.objects.filter(club = self, membership__gte = ClubMembership.UserRoles.MEMBER).count()

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
