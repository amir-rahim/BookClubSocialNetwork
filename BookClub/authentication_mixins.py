from django.shortcuts import redirect
from BookClub.helpers import has_membership, get_club_from_url_name
from django.contrib.auth.mixins import UserPassesTestMixin
from BookClub.models import Club


class LoginProhibitedMixin:
    """
        If user trying to access this view is authenticated, they are redirected to the 'home' page
    """

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)
    
class ClubMemberTestMixin(UserPassesTestMixin):
    
    def test_func(self):
        club_url_name = self.kwargs.get('club_url_name')
        if club_url_name is not None:
            return has_membership(club=get_club_from_url_name(club_url_name), user=self.request.user)
        else:
            return True
