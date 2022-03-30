"""Search table related views."""
from django.http import JsonResponse
from django.template import TemplateDoesNotExist
from django.views.generic import TemplateView
from django.db.models import Q
from django.template.loader import render_to_string
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from BookClub.models import *
from BookClub.views.async_views.search_query_builder import ClubQuery, UserQuery, BookQuery, BookListQuery


class SearchView(TemplateView):
    """Render search table with pagination. Returns rendered template to the user as a JSONResponse which is then displayed using JS.
        Allows for generic searches for any content type that a Query has been created for.
    """
    paginate_by = 10
    search_queries = [ClubQuery, BookQuery, UserQuery, BookListQuery]

    def get(self, request, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        select = request.GET.get('select', False)
        page = request.GET.get('page', 1)
        query = request.GET.get('q', "")
        content_type = request.GET.get('content_type', None)
        content_type = ContentType.objects.get(pk=content_type)

        objects = self.get_queryset(content_type=content_type, query=query)

        if select:
            self.paginate_by = 5
        context['page_obj'] = self.get_pagination(objects, page)
        html = render_to_string(
            template_name=self.get_template_names(content_type=content_type), context=context, request=request)
        data_dict = {"html_from_view": html}
        return JsonResponse(data=data_dict, safe=False)

    def get_queryset(self, query="", content_type=None):
        model = content_type.model_class()
        Qs = self.get_query(model, query)
        obs = model.objects.filter(Qs)
        return obs

    def get_pagination(self, object_list, page=1):
        paginator = Paginator(object_list, self.paginate_by)
        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
        return page_obj

    def get_template_names(self, content_type=None, **kwargs):
        select = self.request.GET.get('select')
        check = self.request.GET.get('check')
        model = content_type.model_class()
        if model == Book:
            if select:
                return ['partials/book_select_list.html']
            if check:
                return ['partials/book_check_list.html']
            return ['partials/book_search_list.html']

        if model == User:
            return ['partials/user_search_list.html']

        if model == Club:
            return ['partials/club_search_list.html']

        if model == BookList:
            return ['partials/booklist_search_list.html']
        
        raise TemplateDoesNotExist("No template found for " + content_type)

    def get_query(self, model, query):
        q_objects = Q()
        for query_class in self.search_queries:
            q_objects = query_class(
                query=query, q_objects=q_objects, model=model).build_query(user=self.request.user)
        return q_objects
