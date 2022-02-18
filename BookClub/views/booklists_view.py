from django.shortcuts import get_object_or_404

from django.views.generic.list import ListView

from BookClub.models.user import User
from BookClub.models.booklist import BookList

class BooklistListView(ListView):
    http_method_names = ['get']
    model = BookList
    context_object_name = 'booklists'
    template_name = 'user_booklists.html'

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs['username'])
        print(f"Found the user: {user.username}")
        return BookList.objects.filter(creator = user)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        print(f"done context. lists: {str(list(context['booklists']))}")
        # Add in a QuerySet of all the books
        creator = User.objects.get(username = self.kwargs['username'])
        context['creator'] = creator
        context['self'] = self.request.user == creator
        return context
