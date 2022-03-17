from django.http import JsonResponse
from django.views.generic import TemplateView  
from django.db.models import Q
from django.template.loader import render_to_string
from BookClub.models import Book

class BookSearchView(TemplateView):
    
    def get(self, request, *args, **kwargs):
        url_parameter = request.GET.get('q')
        context = {}
        if url_parameter:
            query = url_parameter
            object_list = Book.objects.filter(
                Q(title__icontains=query) | Q(author__icontains=query) | Q(
                    publisher__icontains=query)
            )
        else:
            object_list = None
            
        context['books'] = object_list
        if request.is_ajax():
            html = render_to_string(
                template_name='partials/partial_books_list.html', context={'books': object_list})
            data_dict = {"html_from_view" : html}
            return JsonResponse(data=data_dict, safe=False)