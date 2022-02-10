from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import DeleteView
from BookClub.helpers import RankRequiredMixin,get_club_id
from django.urls import reverse_lazy
from BookClub.models import club
from BookClub.models.club import Club
from BookClub.models.club_membership import ClubMembership
from BookClub.models.user import User

#may need to change to just BookClub.models cos of pycharm problem
#may need UserPassesTextMixin for validation (some applicant could somehow get to the delete link)
class DeleteClubView(LoginRequiredMixin, RankRequiredMixin, DeleteView):
    login_url = "login.html"
    redirect_field_name = "redirect"

    model = Club
    success_url = reverse_lazy("delete_club.html")

    raise_exception = False


    requiredRanking = ClubMembership.UserRoles.OWNER

    def setup(self, request, *args, **kwargs):
        self.requiredClub = get_club_id(request)
        return super().setup(request, *args, **kwargs)

    def get_object(self):
        try:
            return Club.get(pk=self.requiredClub)
        except:
            return None



    





