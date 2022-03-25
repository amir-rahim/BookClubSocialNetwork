from django.template import Library
from BookClub.models import ClubMembership
register = Library()

@register.simple_tag(takes_context=True)
def is_member(context, club, user, **kwargs):
    return ClubMembership.objects.filter(club=club, user=user).exists()