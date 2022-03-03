from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin

from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.shortcuts import redirect
from django.urls import reverse_lazy

from django.views.generic import ListView, CreateView, View

from BookClub.models import User, BookList
from BookClub.forms import CreateBookListForm

class BooklistListView(ListView):
    http_method_names = ['get']
    model = BookList
    context_object_name = 'booklists'
    template_name = 'user_booklists.html'

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs['username'])
        return BookList.objects.filter(creator = user)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        creator = User.objects.get(username = self.kwargs['username'])
        context['creator'] = creator
        context['self'] = self.request.user == creator
        context['base_delete_url'] = reverse_lazy('delete_booklist', kwargs={'username' : creator.username})
        return context

class CreateBookListView(LoginRequiredMixin, CreateView):
    template_name = 'create_booklist.html'
    model = BookList
    form_class = CreateBookListForm

    def form_valid(self, form):
        form.instance.creator = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, ('Successfully created a new booklist!'))
        return response

    def form_invalid(self, form):
        messages.add_message(self.request, messages.ERROR, "The data provided was invalid!")
        return super().form_invalid(form)

class DeleteBookListView(LoginRequiredMixin, View):
    http_method_names = ['post']

    def http_method_not_allowed(self, request, *args, **kwargs):
        messages.add_message(self.request, messages.ERROR, "Non-existing page was requested, so we redirected you here...")
        return redirect('booklists_list', username = self.kwargs['username'])

    def post(self, *args, **kwargs):
        user = self.request.user
        try:
            booklist = BookList.objects.get(pk = self.kwargs['list_id'])
            if booklist.creator == user:
                booklist.delete()
                messages.success(self.request, f"Booklist '{booklist.title}' successfully deleted!")
                return redirect('booklists_list', username = self.kwargs['username'])
            else:
                raise PermissionDenied
        except ObjectDoesNotExist:
            messages.add_message(self.request, messages.ERROR, "Non-existing list was targeted")
            return redirect('booklists_list', username = self.kwargs['username'])

class UserBookListView(ListView):
    http_method_names = ['get']
    model = BookList
    context_object_name = 'books'
    template_name = 'booklist.html'

    def get_queryset(self):
        booklist = BookList.objects.get(pk = self.kwargs['booklist_id'])
        subquery = booklist.get_books()
        return subquery

    def get_context_data(self, **kwargs):
        booklist = BookList.objects.get(pk = self.kwargs['booklist_id'])
        context = super().get_context_data(**kwargs)
        context['booklist'] = BookList.objects.get(pk = self.kwargs['booklist_id'])
        context['user'] = self.request.user
        context['number_of_books'] = len(booklist.get_books())
        return context
