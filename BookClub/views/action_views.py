'''Action Related Views'''
from email import message
from multiprocessing import context
from django.views.generic import TemplateView, View, DeleteView
from BookClub.helpers import *
from BookClub.models.club import Club, User
from BookClub.models.user import User
from BookClub.models.club_membership import ClubMembership
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin


class ActionView(TemplateView):
    """Class for views that make an action"""

    def get(self, request, *args, **kwargs):
        return redirect(self.redirect_location, kwargs['url_name'])

    def post(self, request, *args, **kwargs):
        """
        Handle post request

        Args:
            request (Django Request): The request we have received
        """

        try:
            club = Club.objects.get(url_name=self.kwargs['url_name'])
            currentUser = self.request.user
            targetUser = User.objects.get(username=self.request.POST.get('user'))
        except:
            messages.error(self.request, "Error, user or club not found.")

        if (self.is_actionable(currentUser, targetUser, club)):
            self.action(currentUser, targetUser, club)
        else:
            self.is_not_actionable(currentUser, targetUser, club)

        return redirect(self.redirect_location, kwargs['url_name'])

    def is_actionable(self, currentUser, targetUser, club):
        """Check if the action is legal"""

        raise NotImplementedError("This method isn't implemented yet.")

    def is_not_actionable(self, currentUser, targetUser, club):
        """Displays a message if the action is illegal"""

        messages.error(self.request, f"You cannot do that!")

    def action(self, currentUser, targetUser, club):
        """Runs the action"""

        raise NotImplementedError("This method isn't implemented yet.")


class PromoteMemberView(LoginRequiredMixin, ActionView):
    """Promoting a member to a moderator"""

    redirect_location = 'member_list'
    requiredRanking = ClubMembership.UserRoles.OWNER

    def is_actionable(self, currentUser, targetUser, club):
        """Check if member can be promoted."""

        return (has_owner_rank(currentUser, club) and has_member_rank(targetUser, club))

    def action(self, currentUser, targetUser, club):
        """Promotes the member to moderator"""

        messages.success(self.request, f"You have successfully promoted the member.")
        set_rank(targetUser, club, ClubMembership.UserRoles.MODERATOR)

    def post(self, request, *args, **kwargs):
        return super().post(self, request, *args, **kwargs)


class DemoteMemberView(LoginRequiredMixin, ActionView):
    """Demoting a moderator to a member"""

    redirect_location = 'member_list'
    requiredRanking = ClubMembership.UserRoles.OWNER  # check with Jack

    def is_actionable(self, currentUser, targetUser, club):
        """Check if moderator can be demoted"""

        return has_owner_rank(currentUser, club) and has_moderator_rank(targetUser, club)

    def action(self, currentUser, targetUser, club):
        """Demote moderator to a member"""

        messages.success(self.request, f"You have successfully demoted the moderator.")
        set_rank(targetUser, club, ClubMembership.UserRoles.MEMBER)

    def post(self, request, *args, **kwargs):
        return super().post(self, request, *args, **kwargs)


class KickMemberView(LoginRequiredMixin, ActionView):
    """Kicks the target user from the club"""

    redirect_location = 'member_list'
    requiredRanking = ClubMembership.UserRoles.OWNER or ClubMembership.UserRoles.MODERATOR

    def is_actionable(self, currentUser, targetUser, club):
        """Check if currentUser can kick targetUser"""

        return can_kick(club, currentUser, targetUser)

    def action(self, currentUser, targetUser, club):
        """Kick targetUser"""

        messages.success(self.request, f"You have successfully kicked the member.")
        remove_from_club(targetUser, club)

    def post(self, request, *args, **kwargs):
        return super().post(self, request, *args, **kwargs)


class TransferOwnershipView(LoginRequiredMixin, ActionView):
    """Transfer ownership to another moderator"""

    redirect_location = 'member_list'
    requiredRanking = ClubMembership.UserRoles.OWNER

    def is_actionable(self, currentUser, targetUser, club):
        """Check if the ownership can be transferred to a valid moderator"""

        return has_owner_rank(currentUser, club) and has_moderator_rank(targetUser, club)

    def action(self, currentUser, targetUser, club):
        """Transfer ownership to moderator and demote owner to moderator"""

        messages.success(self.request, f"You have transferred the ownership successfully.")
        set_rank(targetUser, club, ClubMembership.UserRoles.OWNER)
        set_rank(currentUser, club, ClubMembership.UserRoles.MODERATOR)

    def post(self, request, *args, **kwargs):
        return super().post(self, request, *args, **kwargs)


class JoinClubView(LoginRequiredMixin, View):
    """Users can join/apply to clubs"""

    redirect_location = 'available_clubs'

    def is_actionable(self, currentUser, club):
        """Check if user can join/apply to a club"""

        return not has_membership(club, currentUser)

    def is_not_actionable(self, currentUser, club):
        """If user has a membership with the club already"""

        if is_club_private(club):
            messages.info(self.request, "You have already applied to this club.")
        else:
            messages.info(self.request, "You are already a member of this club.")

    def action(self, currentUser, club):
        """Create membership for user with the club depending on privacy"""

        if is_club_private(club):
            create_membership(club, currentUser, ClubMembership.UserRoles.APPLICANT)
            messages.success(self.request, "Application to club successful.")
        else:
            create_membership(club, currentUser, ClubMembership.UserRoles.MEMBER)
            messages.success(self.request, "You have joined the club.")

    def post(self, request, *args, **kwargs):

        try:
            club = Club.objects.get(url_name=self.kwargs['url_name'])
            currentUser = self.request.user
        except:
            messages.error(self.request, "Error, user or club not found.")

        if (self.is_actionable(currentUser, club)):
            self.action(currentUser, club)
        else:
            self.is_not_actionable(currentUser, club)

        return redirect(self.redirect_location)


class LeaveClubView(LoginRequiredMixin, View):
    """User can leave their club"""

    redirect_location = 'my_club_memberships'

    def is_actionable(self, currentUser, club):
        """Check if currentUser is in the club"""

        return has_membership(club, currentUser) and not (
                has_applicant_rank(currentUser, club) or has_owner_rank(currentUser, club))

    def is_not_actionable(self, currentUser, club):
        """If the user is unable to leave the club"""

        if has_owner_rank(currentUser, club):
            messages.error(self.request, "The owner of the club cannot leave.")
        if has_applicant_rank(currentUser, club):
            messages.error(self.request, "You can't leave as an applicant.")

    def action(self, currentUser, club):
        """User leaves the club, membership with the club is deleted"""

        messages.success(self.request, "You have left the club.")
        remove_from_club(currentUser, club)

    def post(self, request, *args, **kwargs):

        try:
            club = Club.objects.get(url_name=self.kwargs['url_name'])
            currentUser = self.request.user
        except:
            messages.error(self.request, "Error, user or club not found.")

        if (self.is_actionable(currentUser, club)):
            self.action(currentUser, club)
        else:
            self.is_not_actionable(currentUser, club)

        return redirect(self.redirect_location)

#Still unsure about where to redirect in successful/unsuccessful action
class DeleteClubView(LoginRequiredMixin,View):

    redirect_location = 'available_clubs'
    
    
    def is_actionable(self,currentUser,club):
        return has_owner_rank(currentUser,club)

    def is_not_actionable(self):

        messages.error(self.request, f"You are not allowed to delete the club!")

    def action(self,currentUser,club):
        delete_club(club)
        messages.success(self.request, "You have deleted the club.")


    def post(self, request, *args, **kwargs):
        try:
            club = Club.objects.get(url_name=self.kwargs['url_name'])
            currentUser = self.request.user
        except:
            messages.error(self.request, "Error, user or club not found.")
        if self.is_actionable(currentUser,club):
            self.action(currentUser,club)
            return redirect(self.redirect_location)
        else:
            self.is_not_actionable()
        #Redirects to home if user cannot delete club
        return redirect('home')