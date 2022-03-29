from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.views.generic import ListView, View

from BookClub.models import User, BookList

class SavedBooklistsListView(LoginRequiredMixin, ListView):
    http_method_names = ['get']
    model = BookList
    context_object_name = 'booklists'
    template_name = 'booklists/saved_booklists.html'

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