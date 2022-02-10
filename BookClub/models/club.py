from django.db import IntegrityError, models
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

    # Has unimplemented dependencies
    def get_number_of_meetings(self):
        pass

    # Has unimplemented dependencies
    def get_number_of_posts(self):
        pass

    # Has unimplemented dependencies
    def get_review_score(self):
        pass
    
    def add_user(self, user, rank):
        try:
            ClubMembership.objects.create(
                user = user,
                club = self,
                membership = rank,
            )
        except IntegrityError:
            pass

    def add_member(self, user):
        self.add_user(user, ClubMembership.UserRoles.MEMBER)
        
    def add_moderator(self, user):
        self.add_user(user, ClubMembership.UserRoles.MODERATOR)
        
    def add_owner(self, user):
        if not (ClubMembership.objects.filter(club=self, membership=ClubMembership.UserRoles.OWNER).exists()):
            self.add_user(user, ClubMembership.UserRoles.OWNER)
        else:
            #print("Owner already set")
            pass
    def add_applicant(self, user):
        self.add_user(user, ClubMembership.UserRoles.APPLICANT)
    
    def remove_from_club(self, user):
        try:
            ClubMembership.objects.filter(user=user, club=self).delete()
        except:
            pass