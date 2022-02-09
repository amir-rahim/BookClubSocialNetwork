''''Actions Related Views'''
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View, DeleteView
from django.shortcuts import get_object_or_404
from BookClub.models.club_membership import ClubMembership
from BookClub.models.club import Club
from BookClub.models.user import User


class JoinClubView(LoginRequiredMixin, View):
    """Users can join or apply to clubs depending on the privacy settings of the club"""

    def post(self, request, club_id):
        user_instance = User.objects.get(id=request.user.id)

        try:
            club_instance = Club.objects.get(id=club_id)
        except Club.DoesNotExist:
            messages.add_message(request, messages.ERROR, "Club does not exist!")
            return redirect('available_clubs')

        try:
            ClubMembership.objects.get(user=user_instance, club=club_instance)
        except ClubMembership.DoesNotExist:
            if (club_instance.is_private == True):
                new_membership = ClubMembership(user=user_instance, club=club_instance)
                new_membership.save()
                messages.add_message(request, messages.SUCCESS, "Application to club successful!")
                return redirect('available_clubs')
            else:
                new_membership = ClubMembership(user=user_instance, club=club_instance, membership=ClubMembership.UserRoles.MEMBER)
                new_membership.save()
                messages.add_message(request, messages.SUCCESS, "You have joined the club!")
                return redirect('available_clubs')
        else:
            if (club_instance.is_private == True):
                messages.add_message(request, messages.INFO, "You have already applied to this club!")
                return redirect('available_clubs')

        messages.add_message(request, messages.INFO, "You are already a member of this club!")
        return redirect('available_clubs')


class LeaveClubView(LoginRequiredMixin, DeleteView):
    """Users can leave their club"""

    model = ClubMembership
    success_url = '/my_club_memberships/'

    def get_object(self):
        club_instance = Club.objects.get(id=self.kwargs.get('club_id'))
        user_instance = User.objects.get(id=self.request.user.id)
        return get_object_or_404(ClubMembership, club=club_instance, user=user_instance)
