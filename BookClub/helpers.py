
from django.conf import settings
from django.shortcuts import redirect
from BookClub.models.club import Club
from BookClub.models.club_membership import ClubMembership
from django.contrib import messages
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
    Set requiredRanking to be a ClubMembership userrole. requiredClub is set automatically.
    
    """
    requiredRanking = ClubMembership.UserRoles.OWNER
    requiredClub = -1
    
    def setup(self, request, *args, **kwargs):
        self.requiredClub = get_club_id(request)
        return super().setup(request, *args, **kwargs)
    
    def dispatch(self, request, *args, **kwargs):
        try:
            club_membership = ClubMembership.objects.get(Q(club=self.requiredClub)&Q(user=request.user))
        except ClubMembership.DoesNotExist:
            messages.add_message(request, messages.ERROR, "You are not a member of that club!")
            return redirect('home')
        if club_membership is not None and club_membership.membership == self.requiredRanking:
            return super().dispatch(request, *args, **kwargs)
        else:
            messages.add_message(request, messages.ERROR, "You are not the required rank!")
            return redirect('home')
        
        
def get_club_id(request):
    """ Helper to access session['club_id'] in a safe way

    Args:
        request (request)): The http request object we're accessing

    Returns:
        Int: primary key of the club the user is currently viewing. Returns -1 if club doesn't exist or club_id isn't set
    """
    try:
        id = request.session['club_id']
        club = Club.objects.get(pk=id)
        return id
    except:
        return -1