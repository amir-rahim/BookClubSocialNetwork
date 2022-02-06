''''Actions Related Views'''
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from BookClub.models.club_membership import ClubMembership
from BookClub.models.club import Club
from BookClub.models.user import User

@login_required
def apply_to_club(request, club_id):
    """"User can apply to join a club which they are not a member of"""
    club_instance = Club.objects.get(id=club_id)
    user_instance = User.objects.get(id=request.user.id)
    try:
        ClubMembership.objects.get(user=user_instance, club=club_instance)
    except ClubMembership.DoesNotExist:
        new_membership = ClubMembership(user=user_instance, club=club_instance)
        new_membership.save()
        messages.add_message(request, messages.SUCCESS, "Application to club successful!")
        return redirect('available_clubs')

    messages.add_message(request, messages.SUCCESS, "You have already applied to this club!")

    return redirect('available_clubs')
