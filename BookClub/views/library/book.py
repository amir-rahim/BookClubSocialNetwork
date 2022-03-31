"""Book related views."""
from django.views.generic import DetailView, ListView
from django.shortcuts import get_object_or_404
from BookClub.models import Book, BookReview, BookList, BookShelf


class BookDetailView(DetailView):
    """Render the details, reviews and actions for a book."""
    model = Book
    template_name = 'library/book_detail_view.html'
    pk_url_kwarg = 'book_id'
    context_object_name = 'book'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        book = context.get('book')
        user = self.request.user

        if not user.is_anonymous:
            context['lists'] = BookList.objects.filter(creator=user)
            context['user'] = user
            context['in_bookshelf'] = BookShelf.objects.filter(user=self.request.user, book=book).exists()
        else:
            context['lists'] = None
            context['user'] = None
            context['in_bookshelf'] = False

        reviews = BookReview.objects.filter(book=book)
        if reviews:
            context['reviews'] = reviews[:3]
            sum = 0
            for review in reviews:
                sum += review.book_rating
            avg = sum / len(reviews)
            avg = round(avg, 2)
            context['average'] = avg
            if len(reviews) > 3:
                context['more'] = True
        else:
            reviews = None

        return context


class BookReviewListView(ListView):
    """Render a table of reviews for a given book."""
    model = BookReview
    template_name = 'library/book_reviews.html'
    context_object_name = 'reviews'
    paginate_by = 10

    def get_queryset(self):
        book_pk = self.kwargs.get('book_id')
        book = get_object_or_404(Book, pk=book_pk)
        queryset = BookReview.objects.filter(book = book).order_by('-id')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        book_pk = self.kwargs.get('book_id')
        book = Book.objects.get(pk=book_pk)
        context['book'] = book

        return context
