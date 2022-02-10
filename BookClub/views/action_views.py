from django.views.generic import TemplateView
from BookClub.helpers import *
from BookClub.models.club import Club, User
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages

class ActionView(TemplateView):
    
    redirect_location = reverse('home')
    
    def get(self, club, user, request, *args, **kwargs):
        """
        Handle get request

        Args:
            request (Django Request): The request we have recieved
        """
        try:
            club = Club.objects.get(pk=club);
            currentUser = request.user
            targetUser = User.objects.get(pk=user)
        except:
            messages.error(request, "Error, user or club not found")
            
        if(self.is_actionable(currentUser, targetUser, club)):
            self.action(currentUser, targetUser, club)
        
        return redirect(self.redirect_location)
    
    def is_actionable(currentUser, targetUser, club):
        raise NotImplementedError("This method isn't implented yet.")
    
    def action(currentUser, targetUser, club):
        raise NotImplementedError("This method isn't implemented yet.")

"""
Class view for promoting members.
"""
class PromoteView(ActionView,RankRequiredMixin):

    """
    Check if the action is legal
    """
    def is_actionable(currentUser, targetUser, club):
        #check if user is an owner, and the target user is of type member and nothing else. 
        #first check if they are part of the same club.
        return (has_owner_rank(currentUser,club) and has_member_rank(targetUser,club))

    class DemoteMemberView(RankRequiredMixin, ActionView):
        """Demoting member to a moderator"""

        redirect_location = 'members_list'

        def is_actionable(current_user, targetUser, club):
            """Check if moderator can be demoted."""

            return has_owner_rank(current_user, club) and has_moderator_rank(targetUser, club)

        def action(current_user, targetUser, club):
            """Demote moderator to a member."""
            messages.success(self.request, f"You have demoted the moderator successfully")
            set_rank(targetUser, club, "MEMBER")

        def get(self, request, *args, **kwargs):
            """Handle get request."""

            return super().get(request, *args, **kwargs)