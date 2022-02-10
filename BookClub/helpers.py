from django.conf import settings
from django.shortcuts import redirect
from BookClub.models.club import Club
from BookClub.models.club_membership import ClubMembership
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist

from BookClub.models.user import User


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
            club_membership = ClubMembership.objects.get(Q(club=self.requiredClub) & Q(user=request.user))
        except ClubMembership.DoesNotExist:

            return redirect('home')
        if club_membership is not None:
            if club_membership.membership == self.requiredRanking:
                return super().dispatch(request, *args, **kwargs)
        else:
            return redirect('home')


def get_club_id(request):
    try:
        id = request.session['club']
        club = Club.objects.get(pk=id)
        return id
    except:
        return -1


"""
Helpers for checking the authentication level of the user.
"""   
#Used to get the actual rank of the user (if they have a membership in that club)
def get_rank(user,club):
    try:
        rank = ClubMembership.objects.get(user = user, club = club).membership
        return rank
    except ObjectDoesNotExist:
        return None

def set_rank(user,club,rank):
    membership = ClubMembership.objects.filter(user = user, club=club).update(membership = rank)


def has_owner_rank(user,club):
    rank = get_rank(user,club)
    if rank is not None:
        return rank == ClubMembership.UserRoles.OWNER
    else:
        return False
    

def has_member_rank(user,club):
    rank = get_rank(user,club)
    if rank is not None:
        return rank == ClubMembership.UserRoles.MEMBER
    else:
        return False
    

def has_moderator_rank(user,club):
    rank = get_rank(user,club)
    if rank is not None:
        return rank == ClubMembership.UserRoles.MODERATOR
    else:
        return False

def has_applicant_rank(user,club):
    rank = get_rank(user,club)
    if rank is not None:
        return rank == ClubMembership.UserRoles.APPLICANT
    else:
        return False

def remove_from_club(user,club):
    membership = ClubMembership.objects.get(user = user, club=club)
    membership.delete()

"""Helper for checking whether a club is public or private"""
def is_club_private(club):
    return club.is_private

