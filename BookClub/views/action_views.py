from django.views.generic import TemplateView, View
from BookClub.helpers import *
from BookClub.models.club import Club, User
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin


class ActionView(TemplateView):
    redirect_location = 'home'

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

        if (self.is_actionable(currentUser, targetUser, club)):
            self.action(currentUser, targetUser, club)

        return redirect(self.redirect_location)

    def is_actionable(currentUser, targetUser, club):
        """Check if the action is legal"""
        raise NotImplementedError("This method isn't implented yet.")

    def action(currentUser, targetUser, club):
        raise NotImplementedError("This method isn't implemented yet.")


"""Class view for promoting members."""


class PromoteMemberView(RankRequiredMixin, ActionView):
    """Promoting a member to a moderator"""

    redirect_location = 'members_list'
    requiredRanking = ClubMembership.UserRoles.OWNER

    def is_actionable(currentUser, targetUser, club):
        """Check if member can be promoted."""

        return (has_owner_rank(currentUser, club) and has_member_rank(targetUser, club))

    def action(self, currentUser, targetUser, club):
        messages.success(self.request, f"You have promoted the member successfully")
        set_rank(targetUser, club, ClubMembership.UserRoles.MODERATOR)

    def get(self, club, user, request, *args, **kwargs):
        return super().get(club, user, request, *args, **kwargs)


class DemoteMemberView(RankRequiredMixin, ActionView):
    """Demoting a moderator to a member"""

    redirect_location = 'members_list'
    requiredRanking = ClubMembership.UserRoles.OWNER

    def is_actionable(currentUser, targetUser, club):
        """Check if moderator can be demoted."""

        return has_owner_rank(currentUser, club) and has_moderator_rank(targetUser, club)

    def action(self, currentUser, targetUser, club):
        """Demote moderator to a member."""
        messages.success(self.request, f"You have demoted the moderator successfully")
        set_rank(targetUser, club, ClubMembership.UserRoles.MEMBER)

    def get(self, club, user, request, *args, **kwargs):
        return super().get(club, user, request, *args, **kwargs)


class KickMemberView(RankRequiredMixin, ActionView):
    """Promoting member to a moderator"""

    redirect_location = 'members_list'
    requiredRanking = ClubMembership.UserRoles.OWNER or ClubMembership.UserRoles.MODERATOR

    def is_actionable(self, currentUser, targetUser, club):
        """Check if current_user can kick targetUser"""

        return can_kick(club, currentUser, targetUser)

    def action(self, currentUser, targetUser, club):
        """Kick member"""
        messages.success(self.request, f"You have kicked the member")
        remove_from_club(targetUser, club)

    def get(self, club, user, request, *args, **kwargs):
        return super().get(club, user, request, *args, **kwargs)


class TransferOwnershipView(RankRequiredMixin, ActionView):
    """View to transfer ownership to another moderator"""

    redirect_location = 'members_list'
    requiredRanking = ClubMembership.UserRoles.OWNER

    def is_actionable(self, currentUser, targetUser, club):
        """Check if the ownership can be transferred to a valid officer."""

        return has_owner_rank(currentUser, club) and has_moderator_rank(targetUser, club)

    def action(self, currentUser, targetUser, club):
        """Transfer ownership to moderator and demote owner to moderator"""
        messages.success(self.request, f"You have transferred the ownership successfully")
        set_rank(targetUser, club, ClubMembership.UserRoles.OWNER)
        set_rank(currentUser, club, ClubMembership.UserRoles.MODERATOR)

    def get(self, request, *args, **kwargs):
        """Handle get request."""

        return super().get(request, *args, **kwargs)


class JoinClubView(LoginRequiredMixin, View):
    """Users can join or apply to clubs depending on the privacy settings of the club"""

    redirect_location = 'available_clubs'

    def is_actionable(self, currentUser, club):
        """Check if user can join/apply to a club"""

        return not has_membership(club, currentUser)

    def is_not_actionable(self, currentUser, club):
        """If user has a membership with the club already"""

        if is_club_private(club):
            messages.info(self.request, "You have already applied to this club!")
        else:
            messages.info(self.request, "You are already a member of this club!")
        return redirect(self.redirect_location)

    def action(self, currentUser, club):
        """Create membership for user with the club depending on privacy"""

        if is_club_private(club):
            create_membership(club, currentUser, ClubMembership.UserRoles.APPLICANT)
            messages.success(self.request, "Application to club successful!")
        else:
            create_membership(club, currentUser, ClubMembership.UserRoles.MEMBER)
            messages.success(self.request, "You have joined the club!")
        return redirect(self.redirect_location)

    def post(self, request, *args, **kwargs):
        try:
            club = Club.objects.get(pk=self.kwargs.get('club_id'));
            currentUser = request.user
        except:
            messages.error(request, "Error, user or club not found")
            return redirect(self.redirect_location)

        if self.is_actionable(currentUser, club):
            self.action(currentUser, club)
        else:
            self.is_not_actionable(currentUser, club)

        return redirect(self.redirect_location)

    def get(self, request, *args, **kwargs):
        return redirect(self.redirect_location)


class LeaveClubView(LoginRequiredMixin, View):
    """User can leave their club"""

    redirect_location = 'my_club_memberships'

    def is_actionable(self, currentUser, club):
        """Check if current_user is in the club"""

        return has_membership(club, currentUser) and not (
                    has_applicant_rank(currentUser, club) or has_owner_rank(currentUser, club))

    def is_not_actionable(self, currentUser, club):
        """If the user is unable to leave the club"""

        if has_owner_rank(currentUser, club):
            messages.error(self.request, "The owner of the club cannot leave!")
        if has_applicant_rank(currentUser, club):
            messages.error(self.request, "You can't leave as an applicant!")
        return redirect(self.redirect_location)

    def action(self, currentUser, club):
        """User leaves the club, membership with the club is deleted"""

        messages.success(self.request, "You have left the club!")
        remove_from_club(currentUser, club)
        return redirect(self.redirect_location)

    def post(self, request, *args, **kwargs):
        try:
            club = Club.objects.get(pk=self.kwargs.get('club_id'));
            currentUser = request.user
        except:
            messages.error(request, "Error, user or club not found")
            return redirect(self.redirect_location)

        if self.is_actionable(currentUser, club):
            self.action(currentUser, club)
        else:
            self.is_not_actionable(currentUser, club)

        return redirect(self.redirect_location)

    def get(self, request, *args, **kwargs):
        return redirect(self.redirect_location)
