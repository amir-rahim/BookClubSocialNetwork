from django.http import JsonResponse
from django.views.generic import TemplateView  
from django.db.models import Q
from django.template.loader import render_to_string
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from BookClub.models import Book

class BookSearchView(TemplateView):
    
    def get(self, request, *args, **kwargs):
        url_parameter = request.GET.get('q')
        page = request.GET.get('page', 1)
        context = {}
        object_list = None
        
        
        if url_parameter:
            query = url_parameter
            object_list = Book.objects.filter(
                Q(title__icontains=query) | Q(author__icontains=query) | Q(
                    publisher__icontains=query)
            )
            
        paginator = Paginator(object_list, 10)
        
        try:
            books = paginator.page(page)
        except PageNotAnInteger:
            books = paginator.page(1)
        except EmptyPage:
            books = paginator.page(paginator.num_pages)
            
            
        context['books'] = object_list
        if request.is_ajax():
            html = render_to_string(
                template_name='partials/partial_books_list.html', context={'books': books})
            data_dict = {"html_from_view" : html}
            return JsonResponse(data=data_dict, safe=False)