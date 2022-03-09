from urllib.parse import urlencode
from django.template import Library
from django.contrib.contenttypes.models import ContentType

register = Library()


@register.simple_tag(takes_context=True)
def has_user_voted(context, content, user, **kwargs):

    model = ContentType.objects.get_for_model(
        content.__class__)

    votes = model.get_object_for_this_type(pk=content.pk).votes.all()
    return votes.all().filter(creator=user).count() == 1
