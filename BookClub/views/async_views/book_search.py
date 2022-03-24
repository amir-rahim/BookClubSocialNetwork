from django.http import JsonResponse
from django.views.generic import TemplateView  
from django.db.models import Q
from django.template.loader import render_to_string
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.postgres.search import SearchVector
from BookClub.models import *
from BookClub.views.async_views.search_query_builder import SearchQueries

class SearchView(TemplateView):
    
    paginate_by = 20
    
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        select = request.GET.get('select', False)
        page = request.GET.get('page', 1)
        query = request.GET.get('q', None)
        content_type = request.GET.get('content_type', None)
        
        objects = self.get_queryset(content_type=content_type, query=query)
        
        if select:
            self.paginate_by = 5
            
        context['page_obj'] = self.get_pagination(objects, page)
            
        html = render_to_string(
            template_name=self.get_template_names(), context=context, request=request)
        data_dict = {"html_from_view" : html}
        return JsonResponse(data=data_dict, safe=False)
        
    def get_queryset(self, query=None, content_type = None):
        content_type = ContentType.objects.get(pk=content_type)
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
    
    def get_template_names(self):
        select = self.request.GET.get('select')
        content_type = self.request.GET.get('content_type', None)
        
        if select:
            return ['partials/book_select_list.html']
        
        return ['partials/book_search_list.html']
    
    def get_query(self, model, query):
        q_objects = Q()
        for query_class in SearchQueries:
            q_objects = query_class.value(query=query, q_objects=q_objects, model=model,).build_query(user=self.request.user)
        return q_objects
    
        