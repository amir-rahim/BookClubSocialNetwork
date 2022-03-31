from django.template import Library
from django.contrib.contenttypes.models import ContentType
from BookClub.models import BookList
register = Library()


@register.simple_tag(takes_context=True)
def getcontenttype(context, content, **kwargs):

    contenttypepk = ContentType.objects.get_for_model(
        content.__class__).pk
    
    return contenttypepk

@register.simple_tag(takes_context=True)
def get_content_type_from_queryset(context, queryset, **kwargs):
    
    if len(queryset) > 0:
        content = queryset[0]
        return getcontenttype(context, content)
@register.simple_tag(takes_context=True)
def get_book_list_content_type(context, **kwargs):
    
    contenttype= ContentType.objects.get_for_model(BookList)
    
    return contenttype.pk
