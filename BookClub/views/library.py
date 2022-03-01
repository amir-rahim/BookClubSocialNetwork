'''Library Related Views'''
from django.contrib import messages
from django.shortcuts import redirect, render, reverse
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from BookClub.models import Book
from django.db.models import Exists, Q, OuterRef


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
