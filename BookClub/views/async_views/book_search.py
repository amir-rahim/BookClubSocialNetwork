from django.http import JsonResponse
from django.views.generic import TemplateView  
from django.db.models import Q
from django.template.loader import render_to_string
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from BookClub.helpers import get_memberships
from BookClub.models import *

class BookSearchView(TemplateView):
    
    paginate_by = 20
    test = True
    
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        select = request.GET.get('select')
        page = request.GET.get('page', 1)
        query = request.GET.get('q', None)
        content_type = request.GET.get('c', None)
        
        objects = self.get_queryset(content_type=content_type, query=query)
        
        if select:
            self.paginate_by = 5
        if self.test:
            self.paginate_by = 3
        context['page_obj'] = self.get_pagination(objects, page)
        context['lists'] = None
        
        user = self.request.user
        if not user.is_anonymous:
            context['lists'] = BookList.objects.filter(creator=user)        

        html = render_to_string(
            template_name=self.get_template_names(), context=context, request=request)
        data_dict = {"html_from_view" : html}
        return JsonResponse(data=data_dict, safe=False)
        
    def get_queryset(self, query=None, content_type = None):
        #content_type = ContentType.objects.get(pk=content_type)
        model = Club
        Qs = self.build_query(model, query)
        objs = model.objects.filter(Qs)
        if objs.exists():
            return objs
        return model.objects.all()
    
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
        if select:
            return ['partials/book_select_list.html']
        if self.test:
            return ['partials/object_search_list.html']
        return ['partials/book_search_list.html']
    
    def build_query(self, model, query):
        q_objects = Q()
        if(issubclass(model, UserCreatedObject)):
            q_objects.add(Q(creator__username__icontains=query), Q.OR)
        if(issubclass(model, BookList)):
            q_objects.add(Q(title__icontains=query), Q.OR)
            q_objects.add(Q(description__icontains=query), Q.OR)
        if(issubclass(model, ClubMembership)):
            q_objects.add(Q(user__username__icontains=query), Q.OR)
            q_objects.add(Q(club__name__icontains=query), Q.OR)
        if(issubclass(model, Club)):
            clubs = get_memberships(self.request.user)
            q_objects.add(Q(name__icontains=query), Q.OR)
            q_objects.add(Q(description__icontains=query), Q.OR)
            q_objects.add(Q(tagline__icontains=query), Q.OR)
            q_objects.add(Q(rules__icontains=query, pk__in=clubs), Q.OR)
            q_objects.add(Q(clubmembership__user__username=query, pk__in=clubs), Q.OR)
        if(issubclass(model, Book)):
            q_objects.add(Q(title__icontains=query), Q.OR)
            q_objects.add(Q(author__icontains=query), Q.OR)
            q_objects.add(Q(publisher__icontains=query), Q.OR)
        if(issubclass(model, TextPost)):
            q_objects.add(Q(title__icontains=query), Q.OR)
            q_objects.add(Q(content__icontains=query), Q.OR)
        if(issubclass(model, TextComment)):
            q_objects.add(Q(content__icontains=query), Q.OR)
        if(issubclass(model, Meeting)):
            q_objects.add(Q(title__icontains=query), Q.OR)
            q_objects.add(Q(description__icontains=query), Q.OR)
            q_objects.add(Q(organiser__username__icontains=query), Q.OR)
            q_objects.add(Q(club__name__icontains=query),Q.OR)
            q_objects.add(Q(location__icontains=query), Q.OR)
            q_objects.add(Q(book__name__icontains=query), Q.OR)
            q_objects.add(Q(members__username__icontains=query), Q.OR)
        if(issubclass(model, User)):
            q_objects.add(Q(username__icontains=query), Q.OR)
            q_objects.add(Q(email__icontains=query), Q.OR)
            q_objects.add(Q(public_bio__icontains=query), Q.OR)
        return q_objects
