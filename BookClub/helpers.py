"""Helpers for the project."""
from django.core.exceptions import ObjectDoesNotExist

from BookClub.models import ClubMembership, Club, ForumPost, ForumComment, BookReviewComment, BookReview


def get_club_from_url_name(url_name):
    """Getter for Club via Club URL Name."""
    club = Club.objects.filter(club_url_name=url_name)
    if club.exists():
        return club[0]
    else:
        raise ObjectDoesNotExist()


def get_memberships_with_access(user):
    """Getter for memberships that have permissions."""
    if user.is_authenticated:
        return user.clubmembership_set.exclude(membership=ClubMembership.UserRoles.APPLICANT).values_list('club__pk')
    return []


def get_rank(user, club):
    """Getter for rank of member in a club."""
    try:
        rank = ClubMembership.objects.get(user=user, club=club).membership
        return rank
    except ObjectDoesNotExist:
        return None


def set_rank(user, club, rank):
    """Setter for Rank in User Membership."""
    ClubMembership.objects.filter(user=user, club=club).update(membership=rank)


def is_rank(user, club, desired_rank):
    """Checker for rank of user matches desired rank."""
    rank = get_rank(user, club)
    if rank is not None:
        return rank == desired_rank
    else:
        return False


def has_owner_rank(user, club):
    """Checks for if user is owner."""
    return is_rank(user, club, ClubMembership.UserRoles.OWNER)


def has_member_rank(user, club):
    """Checks for if user is member."""
    return is_rank(user, club, ClubMembership.UserRoles.MEMBER)


def has_moderator_rank(user, club):
    """Checks for if user is moderator."""
    return is_rank(user, club, ClubMembership.UserRoles.MODERATOR)


def has_applicant_rank(user, club):
    """Checks for if user is applicant."""
    return is_rank(user, club, ClubMembership.UserRoles.APPLICANT)


def remove_from_club(user, club):
    """Removes user from specified club."""
    membership = ClubMembership.objects.get(user=user, club=club)
    membership.delete()


def can_kick(club, user, target_user):
    """Checks if user can kick."""
    user_rank = get_rank(user, club)
    target_user_rank = get_rank(target_user, club)

    if user_rank == ClubMembership.UserRoles.OWNER and (
            target_user_rank == ClubMembership.UserRoles.MODERATOR or target_user_rank == ClubMembership.UserRoles.MEMBER):
        return True
    if user_rank == ClubMembership.UserRoles.MODERATOR and target_user_rank == ClubMembership.UserRoles.MEMBER:
        return True
    return False


def has_membership(club, user):
    """Checks if user has a membership."""
    if user.is_authenticated:
        return ClubMembership.objects.filter(user=user, club=club).exists()
    else:
        return False


def has_membership_with_access(club, user):
    """Checks if user has a membership."""
    if user.is_authenticated:
        return ClubMembership.objects.exclude(membership=ClubMembership.UserRoles.APPLICANT).filter(user=user,
                                                                                                    club=club).exists()
    else:
        return False


def create_membership(club, user, membership):
    """Creates a membership for user at specified club."""
    new_membership = ClubMembership(
        user=user, club=club, membership=membership)
    new_membership.save()


def get_user_reputation(user):
    """Retrieves user reputation based off post, review and comment ratings."""
    forum_post_rating = 0
    for post in ForumPost.objects.filter(creator=user):
        forum_post_rating += post.get_rating()

    forum_comment_rating = 0
    for post in ForumComment.objects.filter(creator=user):
        forum_comment_rating += post.get_rating()

    review_rating = 0
    for post in BookReview.objects.filter(creator=user):
        review_rating += post.get_rating()

    review_comment_rating = 0
    for post in BookReviewComment.objects.filter(creator=user):
        review_comment_rating += post.get_rating()

    return forum_post_rating + forum_comment_rating + review_rating + review_comment_rating


def get_club_reputation(club):
    """Retrieves club reputation based off members post, review and comment ratings."""
    members = ClubMembership.objects.filter(club=club, membership__gte=ClubMembership.UserRoles.MEMBER)
    rep = 0
    for user in members:
        rep += get_user_reputation(user.user)

    return rep
