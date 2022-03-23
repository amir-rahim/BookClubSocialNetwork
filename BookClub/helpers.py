from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.shortcuts import redirect

from BookClub.models.club import Club
from BookClub.models.club_membership import ClubMembership
from BookClub.models.user import User




"""
Helpers for checking the authentication level of the user.
"""
def get_club_from_url_name(url_name):
    club = Club.objects.filter(club_url_name=url_name)
    if club.exists():
        return club[0]
    else:
        raise ObjectDoesNotExist()
    
    
def get_memberships(user):
    if user.is_authenticated:
        return user.memberships_set().values_list('club__pk')
    return []



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


def can_kick(club, user, target_user):
    user_rank = get_rank(user, club)
    target_user_rank = get_rank(target_user, club)

    if user_rank == ClubMembership.UserRoles.OWNER and (
            target_user_rank == ClubMembership.UserRoles.MODERATOR or target_user_rank == ClubMembership.UserRoles.MEMBER):
        return True
    if user_rank == ClubMembership.UserRoles.MODERATOR and target_user_rank == ClubMembership.UserRoles.MEMBER:
        return True
    return False


def has_membership(club, user):
    if user.is_authenticated:
        return ClubMembership.objects.filter(user=user, club=club).exists()
    else:
        return False
    
def has_membership_with_access(club, user):
    if user.is_authenticated:
        return ClubMembership.objects.exclude(membership=ClubMembership.UserRoles.APPLICANT).filter(user=user, club=club).exists()
    else:
        return False


def create_membership(club, user, membership):
    new_membership = ClubMembership(
        user=user, club=club, membership=membership)
    new_membership.save()
