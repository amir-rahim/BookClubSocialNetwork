from django.conf import settings
from django.shortcuts import redirect
from BookClub.models.club import Club
from BookClub.models.club_membership import ClubMembership
from django.contrib import messages
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


"""
Helpers for checking the authentication level of the user.
"""


# Used to get the actual rank of the user (if they have a membership in that club)
def get_rank(user, club):
    try:
        rank = ClubMembership.objects.get(user=user, club=club).membership
        return rank
    except ObjectDoesNotExist:
        return None


def set_rank(user, club, rank):
    ClubMembership.objects.filter(user=user, club=club).update(membership=rank)


def is_rank(user, club, desired_rank):
    rank = get_rank(user, club)
    if rank is not None:
        return rank == desired_rank
    else:
        return False


def has_owner_rank(user, club):
    return is_rank(user, club, ClubMembership.UserRoles.OWNER)


def has_member_rank(user, club):
    return is_rank(user, club, ClubMembership.UserRoles.MEMBER)


def has_moderator_rank(user, club):
    return is_rank(user, club, ClubMembership.UserRoles.MODERATOR)


def has_applicant_rank(user, club):
    return is_rank(user, club, ClubMembership.UserRoles.APPLICANT)


def remove_from_club(user, club):
    membership = ClubMembership.objects.get(user=user, club=club)
    membership.delete()


"""Helper for checking whether a club is public or private"""


def is_club_private(club):
    return club.is_private


def can_kick(club, user, targetUser):
    userRank = get_rank(user, club)
    targetUserRank = get_rank(targetUser, club)

    if userRank == ClubMembership.UserRoles.OWNER and (
            targetUserRank == ClubMembership.UserRoles.MODERATOR or targetUserRank == ClubMembership.UserRoles.MEMBER):
        return True
    if userRank == ClubMembership.UserRoles.MODERATOR and targetUserRank == ClubMembership.UserRoles.MEMBER:
        return True
    return False


def has_membership(club, user):
    if user.is_authenticated:
        return ClubMembership.objects.filter(user=user, club=club).exists()
    else:
        return False


def create_membership(club, user, membership):
    new_membership = ClubMembership(
        user=user, club=club, membership=membership)
    new_membership.save()


def delete_club(club):
    club.delete()


def delete_meeting(meeting):
    meeting.delete()


def delete_bookreview(review):
    review.delete()
