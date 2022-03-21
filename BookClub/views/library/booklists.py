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


class BooklistListView(LoginRequiredMixin, ListView):
    http_method_names = ['get']
    model = BookList
    context_object_name = 'booklists'
    template_name = 'user_booklists.html'

    def get_queryset(self):
        if self.kwargs.get('username') is not None:
            user = get_object_or_404(User, username=self.kwargs['username'])
        else:
            user = get_object_or_404(User, username=self.request.user)
        return BookList.objects.filter(creator=user)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        if self.kwargs.get('username') is not None:
            creator = User.objects.get(username=self.kwargs['username'])
            context['own'] = False
        else:
            creator = self.request.user
            context['own'] = True
        context['creator'] = creator
        context['base_delete_url'] = reverse_lazy('delete_booklist', kwargs={'username': creator.username})
        context['saved_booklists'] = creator.get_saved_booklists()
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
            user = booklist.creator
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
            return redirect(self.redirect_location)

    def get_success_url(self):
        """Return redirect URL after successful update."""
        messages.success(self.request, "You have updated the book list!")
        return reverse(self.redirect_location)

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
        return redirect('booklists_list')

    def post(self, *args, **kwargs):
        user = self.request.user
        try:
            booklist = BookList.objects.get(pk=self.kwargs['booklist_id'])
            if booklist.creator == user:
                booklist.delete()
                messages.success(self.request, f"Booklist '{booklist.title}' successfully deleted!")
                return redirect('booklists_list')
            else:
                raise PermissionDenied
        except ObjectDoesNotExist:
            messages.add_message(self.request, messages.ERROR, "Non-existing list was targeted")
            return redirect('booklists_list')


class UserBookListView(LoginRequiredMixin, ListView):
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
        context['user'] = self.request.user
        context['number_of_books'] = len(booklist.get_books())
        return context


class RemoveFromBookListView(LoginRequiredMixin, ListView):
    """Users can leave meetings"""

    redirect_location = 'user_booklist'

    def get(self, request, *args, **kwargs):
        return redirect(self.redirect_location, booklist_id=self.kwargs['booklist_id'])

    def is_actionable(self, booklist, book):
        """Check if user can remove a book"""

        return (booklist.get_books().filter(pk=book.id)) and (self.request.user == booklist.creator)

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
            return redirect(self.redirect_location, booklist_id=self.kwargs['booklist_id'])

        if self.is_actionable(booklist, book):
            self.action(booklist, book)
        else:
            self.is_not_actionable()

        return redirect(self.redirect_location, booklist_id=self.kwargs['booklist_id'])


class SavedBooklistsListView(LoginRequiredMixin, ListView):
    http_method_names = ['get']
    model = BookList
    context_object_name = 'booklists'
    template_name = 'saved_booklists.html'

    def get_queryset(self):
        if self.kwargs.get('username') is not None:
            user = get_object_or_404(User, username=self.kwargs['username'])
        else:
            user = self.request.user
        saved_booklists = user.get_saved_booklists()
        return saved_booklists

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        if self.kwargs.get('username') is not None:
            creator = User.objects.get(username=self.kwargs['username'])
            context['own'] = False
        else:
            creator = self.request.user
            context['own'] = True
        context['creator'] = creator
        # context['base_delete_url'] = reverse_lazy('delete_booklist', kwargs={'username': creator.username})
        return context


class SaveBookListView(LoginRequiredMixin, View):
    """Users can save other user's bookl ists"""

    redirect_location = 'user_booklist'

    def get(self, *args, **kwargs):
        return redirect(self.redirect_location, booklist_id=self.kwargs['booklist_id'])

    def is_actionable(self, current_user, booklist):
        """Check if user can save the book list"""

        return (current_user != booklist.creator) and (
            not User.objects.filter(username=current_user.username, saved_booklists=booklist).exists())

    def is_not_actionable(self):
        """If user cannot save the book list"""

        messages.info(self.request, "You cannot save this book list.")

    def action(self, current_user, booklist):
        """User saves the book list"""

        messages.success(self.request, "You have saved the book list.")
        current_user.save_booklist(booklist)

    def post(self, *args, **kwargs):

        try:
            booklist = BookList.objects.get(id=kwargs['booklist_id'])
            current_user = self.request.user
        except:
            messages.error(self.request, "Error, invalid booklist.")
            return redirect(self.redirect_location, booklist_id=self.kwargs['booklist_id'])

        if self.is_actionable(current_user, booklist):
            self.action(current_user, booklist)
        else:
            self.is_not_actionable()

        return redirect(self.redirect_location, booklist_id=self.kwargs['booklist_id'])


class RemoveSavedBookListView(LoginRequiredMixin, View):
    """Users can remove a saved booklist"""

    redirect_location = 'user_booklist'

    def get(self, *args, **kwargs):
        return redirect(self.redirect_location, booklist_id=self.kwargs['booklist_id'])

    def is_actionable(self, booklist):
        """Check if user can save the book list"""

        return (self.request.user != booklist.creator) and (User.objects.filter(username=self.request.user.username, saved_booklists=booklist).exists())

    def is_not_actionable(self):
        """If user cannot remove saved the book list"""

        messages.info(self.request, "You cannot remove this book list from saved.")

    def action(self, booklist):
        """User removes saved book list"""

        messages.success(self.request, "You have removed the book list from saved.")
        self.request.user.remove_from_saved_booklists(booklist)

    def post(self, *args, **kwargs):

        try:
            booklist = BookList.objects.get(id=kwargs['booklist_id'])
            creator = booklist.creator
        except:
            messages.error(self.request, "Error, invalid booklist.")
            return redirect(self.redirect_location, booklist_id=self.kwargs['booklist_id'])

        if self.is_actionable(booklist):
            self.action(booklist)
        else:
            self.is_not_actionable()

        return redirect(self.redirect_location, booklist_id=self.kwargs['booklist_id'])
