from django.http import JsonResponse
from django.views.generic import TemplateView  
from django.db.models import Q
from django.template.loader import render_to_string
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from BookClub.models import Book
from BookClub.models.booklist import BookList

class BookSearchView(TemplateView):
    
    paginate_by = 20
    
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        select = request.GET.get('select')
        page = request.GET.get('page', 1)
        query = request.GET.get('q', None)
        
        books = self.get_queryset(query)
        
        if select:
            self.paginate_by = 5
            
        context['page_obj'] = self.get_pagination(books, page)
        context['lists'] = None
        
        user = self.request.user
        if not user.is_anonymous:
            context['lists'] = BookList.objects.filter(creator=user)        

        if request.is_ajax():
            html = render_to_string(
                template_name=self.get_template_names()[0], context=context, request=request)
            data_dict = {"html_from_view" : html}
            return JsonResponse(data=data_dict, safe=False)
        
    def get_queryset(self, query=None):
        if query is not None:
            return Book.objects.filter(
                Q(title__icontains=query) | Q(author__icontains=query) | Q(
                    publisher__icontains=query)
            )
        return Book.objects.all()
    
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
        
        return ['partials/book_search_list.html']