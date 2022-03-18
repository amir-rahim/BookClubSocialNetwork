from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.template import Library

register = Library()

@register.simple_tag(takes_context=True)
def get_votes_for_object(context, content):
    model = ContentType.objects.get_for_model(
        content.__class__)

    votes = model.get_object_for_this_type(pk=content.pk).votes.all()
    return votes.all()

@register.simple_tag(takes_context=True)
def has_user_voted(context, votes, user, **kwargs):
    return votes.all().filter(creator=user).count() == 1

@register.simple_tag(takes_context=True)
def get_user_vote_type(context, votes, user, **kwargs):
    try:
        vote_type = votes.all().get(creator=user).type
    except ObjectDoesNotExist:
        return None
    return vote_type
