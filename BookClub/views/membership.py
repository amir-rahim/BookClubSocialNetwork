'''Memberships Related Views'''
from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from BookClub.models.club_membership import ClubMembership
from BookClub.models.club import Club
from django.db.models import Exists, Q, OuterRef

@login_required
def available_clubs(request):
    """Show a list of all clubs the user can apply to (all clubs the user is not member of)."""
    # Select clubs the user is not a member of
    subquery = ClubMembership.objects.filter(user=request.user.pk, club=OuterRef('pk'))
    clubs = Club.objects.filter(
        ~Q(Exists(subquery)) |
        Q(Exists(subquery.filter(membership=ClubMembership.UserRoles.APPLICANT)))
    )
    return render(request, 'available_clubs.html', {'clubs': clubs})

@login_required
def my_club_memberships(request):
    """Show a list of all clubs that the user is a member of (or moderator/creator)."""
    # Select clubs the user is a member of
    return render(request, 'home.html')
