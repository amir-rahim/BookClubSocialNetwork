'''Library Related Views'''
from django.contrib import messages
from django.shortcuts import redirect, render, reverse
from django.views.generic import ListView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from BookClub.models import Book, BookList
from django.db.models import Exists, Q, OuterRef
from BookClub.forms import AddBookForm  


def library_dashboard(request):
    """This is the library dashboard view."""
    return render(request, 'library_dashboard.html')


class BookListView(ListView):
    model = Book
    template_name = "library_books.html"
    context_object_name = 'books'
    paginate_by = 20
    
    def post(self, request):
        if request.POST.get('paginate_by'):
            request.session['paginate_setting'] = request.POST['paginate_by']
        if request.POST.get('q'):
            request.session['query'] = request.POST['q']

        return redirect(reverse('library_books', kwargs=self.kwargs))

    def get_paginate_by(self, queryset):
        if self.request.session.get('paginate_setting'):
            return self.request.session.get('paginate_setting')
        else:
            return self.paginate_by

    def get_queryset(self):  # new
        query = self.request.session.get('query')
        try:
            object_list = Book.objects.filter(
                Q(title__icontains=query) | Q(author__icontains=query) | Q(publisher__icontains=query)
            )
        except:
            object_list = Book.objects.all()
        return object_list
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if not user.is_anonymous:
            context['lists'] = BookList.objects.filter(creator = user)
            context['user'] = user
        else:
            context['lists'] = None
            context['user'] = None
        return context

class AddToBookListView(LoginRequiredMixin, FormView):
    model = BookList
    form_class = AddBookForm
    http_method_names = ['post']

    def form_valid(self, form):
        try:
            book = Book.objects.get(pk=self.request.POST.get('books'))
            booklist = BookList.objects.get(pk=self.request.POST.get('id'))
        except:
            book = None
            booklist = None
        
        if booklist is None or book is None:
            messages.error(self.request, "There was an error finding the book or booklist")

        elif (booklist.get_books().filter(pk=book.id)):
            messages.info(self.request, "This book is already in the list")
        else:
            booklist.add_book(book)
            booklist.save()
            messages.success(self.request, "The book has been saved to "+book.title)
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, "There was an error adding the book")
        return super().form_invalid(form)
        
    def get_success_url(self):
        return reverse('library_books')
