'''Memberships Related Views'''
from django.shortcuts import redirect, render
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from BookClub.models import Book
from django.db.models import Exists, Q, OuterRef


def library_dashboard(request):
    """This is the library dashboard view."""
    return render(request, 'library_dashboard.html')


class BookListView(LoginRequiredMixin, ListView):
    model = Book
    template_name = "library_books.html"
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        return Book.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['books'] = self.get_queryset()
        return context
