"""Library Related Views"""
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import redirect, render, reverse
from django.views.generic import ListView, FormView

from BookClub.forms import AddBookForm
from BookClub.models import Book, BookList


def library_dashboard(request):
    """This is the library dashboard view."""
    return render(request, 'library_dashboard.html')


class BookListView(ListView):
    model = Book
    template_name = "library_books.html"
    context_object_name = 'books'
    paginate_by = 20

    def post(self, request):
        if request.POST.get('q'):
            request.session['query'] = request.POST['q']

        return redirect(reverse('library_books', kwargs=self.kwargs))

    def get_queryset(self):  # new
        query = self.request.session.get('query')
        try:
            object_list = Book.objects.filter(
                Q(title__icontains=query) | Q(author__icontains=query) | Q(publisher__icontains=query)
            )
        except:
            object_list = Book.objects.all()
        return object_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if not user.is_anonymous:
            context['lists'] = BookList.objects.filter(creator=user)
            context['user'] = user
        else:
            context['lists'] = None
            context['user'] = None
        return context


class AddToBookListView(LoginRequiredMixin, FormView):
    model = BookList
    form_class = AddBookForm
    http_method_names = ['post']

    def form_valid(self, form):
        try:
            book = Book.objects.get(pk=self.request.POST.get('book'))
            booklist = BookList.objects.get(pk=self.request.POST.get('booklist'))
        except:
            book = None
            booklist = None

        if booklist is None or book is None:
            messages.error(self.request, "There was an error finding the book or booklist")

        elif booklist.get_books().filter(pk=book.id):
            messages.info(self.request, "This book is already in the list")
        else:
            booklist.add_book(book)
            booklist.save()
            messages.success(self.request, "The book has been saved to " + book.title)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('library_books')
