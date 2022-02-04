'''Memberships Related Views'''
from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
#from clubs.models import Membership, Club

@login_required
def available_clubs(request):
    """Show a list of all clubs the user can apply to (all clubs the user is not member of)."""
    # Select clubs the user is not a member of
    """subquery = Membership.objects.filter(user=request.user.pk, club=OuterRef('pk'))
    clubs = Club.objects.filter(
        ~Q(Exists(subquery)) |
        Q(Exists(subquery.filter(user_type=Membership.UserTypes.NON_MEMBER)))
    )
    return render(request, 'available_clubs.html', {'clubs': clubs})"""
    return render(request, 'available_clubs.html')
