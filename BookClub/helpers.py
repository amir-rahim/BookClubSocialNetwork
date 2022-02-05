from django.conf import settings
from django.shortcuts import redirect
from BookClub.models.club_membership import ClubMembership
from django.db.models import Q
class LoginProhibitedMixin:
    """
        If user trying to access this view is authenticated, they are redirected to the 'home' page
    """
    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

class RankRequiredMixin:
    """
    If user is trying to access this view has required rank and is in required club, they continue, otherwise they are redirected to home page
    """
    requiredRanking = ClubMembership.UserRoles.OWNER
    requiredClub = -1
    def dispatch(self, request, *args, **kwargs):
        try:
            club_membership = ClubMembership.objects.get(Q(club=self.requiredClub)&Q(user=request.user))
        except ClubMembership.DoesNotExist:
            return redirect('home')
        if club_membership is not None:
            if club_membership.membership == self.requiredRanking:
                return super().dispatch(request, *args, **kwargs)
        else:
            return redirect('home')
        