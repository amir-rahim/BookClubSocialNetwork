"""Action Related Views"""
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import TemplateView, View

from BookClub.helpers import *
from BookClub.models import Club, User, ClubMembership


class ActionView(TemplateView):
    """Class for views that make an action"""

    def get(self, request, *args, **kwargs):
        return redirect('home')

    def post(self, request, *args, **kwargs):
        """
        Handle post request

        Args:
            request (Django Request): The request we have received
        """

        try:
            club = Club.objects.get(club_url_name=self.kwargs['club_url_name'])
            current_user = self.request.user
            target_user = User.objects.get(username=self.request.POST.get('user'))
        except:
            messages.error(self.request, "Error, user or club not found.")

        if self.is_actionable(current_user, target_user, club):
            self.action(current_user, target_user, club)
        else:
            self.is_not_actionable(current_user, target_user, club)

        return redirect(self.redirect_location, kwargs['club_url_name'])

    def is_actionable(self, current_user, target_user, club):
        """Check if the action is legal"""

        raise NotImplementedError("This method isn't implemented yet.")

    def is_not_actionable(self, current_user, target_user, club):
        """Displays a message if the action is illegal"""

        messages.error(self.request, f"You cannot do that!")

    def action(self, current_user, target_user, club):
        """Runs the action"""

        raise NotImplementedError("This method isn't implemented yet.")


class PromoteMemberView(LoginRequiredMixin, ActionView):
    """Promoting a member to a moderator"""

    redirect_location = 'member_list'

    def is_actionable(self, current_user, target_user, club):
        """Check if member can be promoted."""

        return (has_owner_rank(current_user, club) and has_member_rank(target_user, club))

    def action(self, current_user, target_user, club):
        """Promotes the member to moderator"""

        messages.success(self.request, f"You have successfully promoted the member.")
        set_rank(target_user, club, ClubMembership.UserRoles.MODERATOR)

    def post(self, request, *args, **kwargs):
        return super().post(self, request, *args, **kwargs)


class DemoteMemberView(LoginRequiredMixin, ActionView):
    """Demoting a moderator to a member"""

    redirect_location = 'member_list'

    def is_actionable(self, current_user, target_user, club):
        """Check if moderator can be demoted"""

        return has_owner_rank(current_user, club) and has_moderator_rank(target_user, club)

    def action(self, current_user, target_user, club):
        """Demote moderator to a member"""

        messages.success(self.request, f"You have successfully demoted the moderator.")
        set_rank(target_user, club, ClubMembership.UserRoles.MEMBER)

    def post(self, request, *args, **kwargs):
        return super().post(self, request, *args, **kwargs)


class ApproveApplicantView(LoginRequiredMixin, ActionView):
    """Approving an applicant to a member"""

    redirect_location = 'applicant_list'

    def is_actionable(self, current_user, target_user, club):
        """Check if applicant can be approved."""

        return ((has_owner_rank(current_user, club) or has_moderator_rank(current_user, club)) and has_applicant_rank(
            target_user, club))

    def is_not_actionable(self, current_user, target_user, club):
        """Displays a message if the action is illegal"""

        redirect_location = 'home'
        messages.error(self.request, f"You cannot do that!")

    def action(self, current_user, target_user, club):
        """Approves the applicant to a member"""

        messages.success(self.request, f"You have successfully approved the applicant.")
        set_rank(target_user, club, ClubMembership.UserRoles.MEMBER)

    def post(self, request, *args, **kwargs):
        return super().post(self, request, *args, **kwargs)


class RejectApplicantView(LoginRequiredMixin, ActionView):
    """Rejecting an applicant"""

    redirect_location = 'applicant_list'

    def is_actionable(self, current_user, target_user, club):
        """Check if applicant can be rejected."""

        return ((has_owner_rank(current_user, club) or has_moderator_rank(current_user, club)) and has_applicant_rank(
            target_user, club))

    def is_not_actionable(self, current_user, target_user, club):
        """Displays a message if the action is illegal"""

        redirect_location = 'home'
        messages.error(self.request, f"You cannot do that!")

    def action(self, current_user, target_user, club):
        """Rejects the applicant"""

        messages.success(self.request, f"You have successfully rejected the applicant.")
        remove_from_club(target_user, club)

    def post(self, request, *args, **kwargs):
        return super().post(self, request, *args, **kwargs)


class KickMemberView(LoginRequiredMixin, ActionView):
    """Kicks the target user from the club"""

    redirect_location = 'member_list'

    def is_actionable(self, current_user, target_user, club):
        """Check if currentUser can kick targetUser"""

        return can_kick(club, current_user, target_user)

    def action(self, current_user, target_user, club):
        """Kick targetUser"""

        messages.success(self.request, f"You have successfully kicked the member.")
        remove_from_club(target_user, club)

    def post(self, request, *args, **kwargs):
        return super().post(self, request, *args, **kwargs)


class TransferOwnershipView(LoginRequiredMixin, ActionView):
    """Transfer ownership to another moderator"""

    redirect_location = 'member_list'

    def is_actionable(self, current_user, target_user, club):
        """Check if the ownership can be transferred to a valid moderator"""

        return has_owner_rank(current_user, club) and has_moderator_rank(target_user, club)

    def action(self, current_user, target_user, club):
        """Transfer ownership to moderator and demote owner to moderator"""

        messages.success(self.request, f"You have transferred the ownership successfully.")
        set_rank(target_user, club, ClubMembership.UserRoles.OWNER)
        set_rank(current_user, club, ClubMembership.UserRoles.MODERATOR)

    def post(self, request, *args, **kwargs):
        return super().post(self, request, *args, **kwargs)


class JoinClubView(LoginRequiredMixin, View):
    """Users can join/apply to clubs"""

    redirect_location = 'available_clubs'

    def get(self, request, *args, **kwargs):
        return redirect(self.redirect_location)

    def is_actionable(self, current_user, club):
        """Check if user can join/apply to a club"""

        return not has_membership(club, current_user)

    def is_not_actionable(self, current_user, club):
        """If user has a membership with the club already"""

        if is_club_private(club):
            messages.info(self.request, "You have already applied to this club.")
        else:
            messages.info(self.request, "You are already a member of this club.")

    def action(self, current_user, club):
        """Create membership for user with the club depending on privacy"""

        if is_club_private(club):
            create_membership(club, current_user, ClubMembership.UserRoles.APPLICANT)
            messages.success(self.request, "Application to club successful.")
        else:
            create_membership(club, current_user, ClubMembership.UserRoles.MEMBER)
            messages.success(self.request, "You have joined the club.")

    def post(self, request, *args, **kwargs):

        try:
            club = Club.objects.get(club_url_name=self.kwargs['club_url_name'])
            current_user = self.request.user
        except:
            messages.error(self.request, "Error, user or club not found.")
            return redirect(self.redirect_location)

        if (self.is_actionable(current_user, club)):
            self.action(current_user, club)
        else:
            self.is_not_actionable(current_user, club)

        return redirect(self.redirect_location)


class LeaveClubView(LoginRequiredMixin, View):
    """User can leave their club"""

    redirect_location = 'my_club_memberships'

    def get(self, request, *args, **kwargs):
        return redirect(self.redirect_location)

    def is_actionable(self, current_user, club):
        """Check if currentUser is in the club"""

        return has_membership(club, current_user) and not (
                has_applicant_rank(current_user, club) or has_owner_rank(current_user, club))

    def is_not_actionable(self, current_user, club):
        """If the user is unable to leave the club"""

        if has_owner_rank(current_user, club):
            messages.error(self.request, "The owner of the club cannot leave.")
        if has_applicant_rank(current_user, club):
            messages.error(self.request, "You can't leave as an applicant.")

    def action(self, current_user, club):
        """User leaves the club, membership with the club is deleted"""

        messages.success(self.request, "You have left the club.")
        remove_from_club(current_user, club)

    def post(self, request, *args, **kwargs):

        try:
            club = Club.objects.get(club_url_name=self.kwargs['club_url_name'])
            current_user = self.request.user
        except:
            messages.error(self.request, "Error, user or club not found.")
            return redirect(self.redirect_location)

        if (self.is_actionable(current_user, club)):
            self.action(current_user, club)
        else:
            self.is_not_actionable(current_user, club)

        return redirect(self.redirect_location)


# Still unsure about where to redirect in successful/unsuccessful action
class DeleteClubView(LoginRequiredMixin, View):
    redirect_location = 'available_clubs'

    def is_actionable(self, current_user, club):
        return has_owner_rank(current_user, club)

    def is_not_actionable(self):

        messages.error(self.request, f"You are not allowed to delete the club!")

    def action(self, current_user, club):
        delete_club(club)
        messages.success(self.request, "You have deleted the club.")

    def post(self, request, *args, **kwargs):
        try:
            club = Club.objects.get(club_url_name=self.kwargs['club_url_name'])
            current_user = self.request.user
            if self.is_actionable(current_user, club):
                self.action(current_user, club)
                return redirect(self.redirect_location)
            else:
                self.is_not_actionable()
        except:
            messages.error(self.request, "Error, user or club not found.")

        # Redirects to home if user cannot delete club
        return redirect('home')
