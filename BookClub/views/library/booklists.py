from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import reverse
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, View, UpdateView

from BookClub.forms import CreateBookListForm
from BookClub.models import User, BookList, Book


class BooklistListView(ListView):
    http_method_names = ['get']
    model = BookList
    context_object_name = 'booklists'
    template_name = 'user_booklists.html'

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs['username'])
        return BookList.objects.filter(creator=user)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        creator = User.objects.get(username=self.kwargs['username'])
        user = self.request.user
        context['creator'] = creator
        context['self'] = self.request.user == creator
        context['base_delete_url'] = reverse_lazy('delete_booklist', kwargs={'username': creator.username})
        context['saved_booklists'] = user.get_saved_booklists()
        return context


class CreateBookListView(LoginRequiredMixin, CreateView):
    template_name = 'create_booklist.html'
    model = BookList
    form_class = CreateBookListForm

    def form_valid(self, form):
        form.instance.creator = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, 'Successfully created a new booklist!')
        return response

    def form_invalid(self, form):
        messages.add_message(self.request, messages.ERROR, "The data provided was invalid!")
        return super().form_invalid(form)


class EditBookListView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = BookList
    form_class = CreateBookListForm
    template_name = 'edit_booklist.html'
    context_object_name = 'booklist'
    redirect_location = 'booklists_list'

    def test_func(self):
        try:
            booklist = BookList.objects.get(pk=self.kwargs['booklist_id'])
            user = User.objects.get(username=self.kwargs['username'])
            if self.request.user == user:
                return True
            else:
                messages.error(self.request, 'You are not the creator of this book list!')
                return False
        except:
            messages.error(self.request, 'Book list not found!')
            return False

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super(LoginRequiredMixin, self).handle_no_permission()
        else:
            return redirect(self.redirect_location, self.kwargs['username'])

    def get_success_url(self):
        """Return redirect URL after successful update."""
        messages.success(self.request, "You have updated the book list!")
        return reverse(self.redirect_location, kwargs={'username': self.kwargs['username']})

    def get_object(self):
        return BookList.objects.get(id=self.kwargs['booklist_id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        booklist = self.get_object()
        context['booklist'] = booklist
        context['id'] = booklist.id
        return context


class DeleteBookListView(LoginRequiredMixin, View):
    http_method_names = ['post']

    def http_method_not_allowed(self, request, *args, **kwargs):
        messages.add_message(self.request, messages.ERROR,
                             "Non-existing page was requested, so we redirected you here...")
        return redirect('booklists_list', username=self.kwargs['username'])

    def post(self, *args, **kwargs):
        user = self.request.user
        try:
            booklist = BookList.objects.get(pk=self.kwargs['list_id'])
            if booklist.creator == user:
                booklist.delete()
                messages.success(self.request, f"Booklist '{booklist.title}' successfully deleted!")
                return redirect('booklists_list', username=self.kwargs['username'])
            else:
                raise PermissionDenied
        except ObjectDoesNotExist:
            messages.add_message(self.request, messages.ERROR, "Non-existing list was targeted")
            return redirect('booklists_list', username=self.kwargs['username'])


class UserBookListView(ListView):
    http_method_names = ['get']
    model = BookList
    context_object_name = 'books'
    template_name = 'booklist.html'

    def get_queryset(self):
        booklist = BookList.objects.get(pk=self.kwargs['booklist_id'])
        subquery = booklist.get_books()
        return subquery

    def get_context_data(self, **kwargs):
        booklist = BookList.objects.get(pk=self.kwargs['booklist_id'])
        context = super().get_context_data(**kwargs)
        context['booklist'] = booklist
        context['user'] = User.objects.get(username=self.kwargs['username'])
        context['number_of_books'] = len(booklist.get_books())
        return context


class RemoveFromBookListView(LoginRequiredMixin, ListView):
    """Users can leave meetings"""

    redirect_location = 'user_booklist'

    def get(self, request, *args, **kwargs):
        return redirect(self.redirect_location, username=self.kwargs['username'],
                        booklist_id=self.kwargs['booklist_id'])

    def is_actionable(self, booklist, book):
        """Check if user can remove a book"""

        return ((booklist.get_books().filter(pk=book.id)) and (self.request.user == booklist.creator))

    def is_not_actionable(self):
        """If user cannot remove book"""

        return messages.info(self.request, "You cannot remove that book!")

    def action(self, booklist, book):
        """User removes the book"""

        messages.success(self.request, "You have removed the book.")
        booklist.remove_book(book)

    def post(self, *args, **kwargs):

        try:
            booklist = BookList.objects.get(id=self.kwargs['booklist_id'])
            book = Book.objects.get(id=self.kwargs['book_id'])
        except:
            messages.error(self.request, "Error, book or booklist not found.")
            return redirect(self.redirect_location, username=self.kwargs['username'],
                            booklist_id=self.kwargs['booklist_id'])

        if self.is_actionable(booklist, book):
            self.action(booklist, book)
        else:
            self.is_not_actionable()

        return redirect(self.redirect_location, username=self.kwargs['username'],
                        booklist_id=self.kwargs['booklist_id'])
