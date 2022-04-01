from django.shortcuts import redirect
from BookClub.helpers import has_membership, get_club_from_url_name, has_membership_with_access
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
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
        try:
            club_url_name = self.kwargs.get('club_url_name')
            if club_url_name is not None:
                return has_membership(club=get_club_from_url_name(club_url_name), user=self.request.user)
            else:
                return True
        except ObjectDoesNotExist:
            return False



class PrivateClubMixin(UserPassesTestMixin):

    def test_func(self):
        try:
            url_name = self.kwargs.get('club_url_name')
            current_club = get_club_from_url_name(url_name)
            if current_club.is_private and not has_membership_with_access(current_club, self.request.user):
                messages.add_message(
                    self.request, messages.ERROR, 'This club is private')
                return False
            else:
                return True
        except ObjectDoesNotExist:
            return False

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        else:
            return redirect('available_clubs')
