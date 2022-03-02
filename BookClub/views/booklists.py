from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin

from django.views.generic import ListView, CreateView

from BookClub.models import User, BookList
from BookClub.forms import CreateBookListForm


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
        messages.success(self.request, 'Successfully created a new booklist!')
        return response

    def form_invalid(self, form):
        messages.add_message(self.request, messages.ERROR, "The data provided was invalid!")
        return super().form_invalid(form)
