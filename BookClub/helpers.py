from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, Sum
from django.shortcuts import redirect

from BookClub.models import User, ClubMembership, Club, ForumPost, ForumComment, BookReviewComment, BookReview

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
    
def get_clubs_user_is_member_of(user):
    return ClubMembership.objects.filter(user=user).values_list('club__pk')


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


def get_user_reputation(user):
    forum_post_rating = ForumPost.objects.filter(creator=user).aggregate(Sum('rating'))
    forum_comment_rating = ForumComment.objects.filter(creator=user).aggregate(Sum('rating'))
    review_rating = BookReview.objects.filter(creator=user).aggregate(Sum('rating'))
    review_comment_rating = BookReviewComment.objects.filter(creator=user).aggregate(Sum('rating'))

    return ((forum_post_rating["rating__sum"] or 0) + (forum_comment_rating["rating__sum"] or 0)
            + (review_rating["rating__sum"] or 0) + (review_comment_rating["rating__sum"] or 0))

def get_club_reputation(club):
    members = ClubMembership.objects.filter(club=club, membership__gte=ClubMembership.UserRoles.MEMBER)
    rep = 0
    for user in members:
        rep += get_user_reputation(user.user)

    return rep
