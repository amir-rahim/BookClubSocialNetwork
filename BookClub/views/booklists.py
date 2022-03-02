from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from django.views.generic import ListView, CreateView, UpdateView
from django.shortcuts import reverse, redirect

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
