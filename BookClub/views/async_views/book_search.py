from django.http import JsonResponse
from django.views.generic import TemplateView  
from django.db.models import Q
from django.template.loader import render_to_string
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from BookClub.models import Book
from BookClub.models.booklist import BookList

class BookSearchView(TemplateView):
    
    def get(self, request, *args, **kwargs):
        url_parameter = request.GET.get('q')
        select = request.GET.get('select')
        page = request.GET.get('page', 1)
        context = {}
        books = None
        
        if url_parameter:
            query = url_parameter
            books = Book.objects.filter(
                Q(title__icontains=query) | Q(author__icontains=query) | Q(
                    publisher__icontains=query)
            )
            
            paginate_by = 10
            
            if select:
                paginate_by = 5
            
            user = self.request.user
            if not user.is_anonymous:
                context['lists'] = BookList.objects.filter(creator=user)
                context['user'] = user
            else:
                context['lists'] = None
                context['user'] = None
    
            paginator = Paginator(books, paginate_by)
            
            try:
                books = paginator.page(page)
            except PageNotAnInteger:
                print("not int")
                books = paginator.page(1)
            except EmptyPage:
                print("empty")
                books = paginator.page(paginator.num_pages)
        else:
            books = Book.objects.all()
        context['books'] = books
        
        if request.is_ajax():
            html = render_to_string(
                template_name=self.get_template_names()[0], context=context)
            data_dict = {"html_from_view" : html}
            return JsonResponse(data=data_dict, safe=False)
        
    def get_template_names(self):
        select = self.request.GET.get('select')
        
        if select:
            return ['partials/book_select_list.html']
        
        return ['partials/book_search_list.html']