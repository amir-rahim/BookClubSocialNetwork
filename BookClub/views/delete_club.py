from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import DeleteView
from BookClubSocialNetwork.BookClub.helpers import RankRequiredMixin,get_club_id
from django.urls import reverse_lazy
from BookClubSocialNetwork.BookClub.models.club import Club
from BookClubSocialNetwork.BookClub.models.club_membership import ClubMembership
from BookClubSocialNetwork.BookClub.models.user import User

#may need to change to just BookClub.models cos of pycharm problem
#may need UserPassesTextMixin for validation (some applicant could somehow get to the delete link)
class DeleteClubView(LoginRequiredMixin, RankRequiredMixin, DeleteView):
    login_url = "login.html"
    redirect_field_name = "redirect"

    model = Club
    success_url = reverse_lazy("delete_club.html")

    raise_exception = False


    requiredRanking = ClubMembership.UserRoles.OWNER
    #verify login
    #if not verified as owner then send back to some page.
    #do the update
    #return to some page.


    def setup(self, request, *args, **kwargs):
        self.requiredClub = get_club_id(request)
        return super().setup(request, *args, **kwargs)




    # def delete(self, request,clubid):
    #     user = request.user
    #
    #     self.dispatch(request,)
    #     if ClubMembership.objects.get(clubid=clubid,user_id=user.id):
    #         #should work
    #         pass
    #     try:
    #         club = Club.objects.get(id=clubid)
    #         #render form, then get input from form and deal with that
    #         club.delete()
    #     except:
    #         pass





