"""View for the bookshelf."""
from django.contrib import messages
from django.views.generic import View, ListView
from django.shortcuts import redirect, reverse
from django.contrib.auth.mixins import LoginRequiredMixin

from BookClub.models import BookShelf, Book


class BookShelfView(LoginRequiredMixin, ListView):
    """Render the user's bookshelf."""
    model = BookShelf
    template_name = 'library/bookshelf.html'
    context_object_name = 'all_books'
    paginate_by = 10
    
    def get_queryset(self):
        subquery = BookShelf.get_all_books(self.request.user)
        return subquery
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['to_read'] = BookShelf.get_to_read(self.request.user)
        context['currently_reading'] = BookShelf.get_reading(self.request.user)
        context['completed'] = BookShelf.get_completed(self.request.user)
        context['on_hold'] = BookShelf.get_on_hold(self.request.user)
        return context

