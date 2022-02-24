from urllib.parse import urlencode
from django.template import Library

register = Library()


@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    query = context['request'].GET.copy()
    if query.get('page'):
        query.pop('page')
    query.update(kwargs)
    return query.urlencode()
