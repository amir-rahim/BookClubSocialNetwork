"""Book Related Views"""
from django.views.generic import DetailView, ListView

from BookClub.models import Book, BookReview


class BookDetailView(DetailView):
    model = Book
    template_name = 'book_detail_view.html'
    pk_url_kwarg = 'book_id'
    context_object_name = 'book'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        book = context.get('book')
        if book is not None:
            reviews = BookReview.objects.filter(book=book)
            if reviews:
                context['reviews'] = reviews[:3]
                sum = 0
                for review in reviews:
                    sum += review.rating
                avg = sum / len(reviews)
                avg = round(avg, 2)
                context['average'] = avg
                if len(reviews) > 3:
                    context['more'] = True
            else:
                reviews = None
        return context


class BookReviewListView(ListView):
    model = BookReview
    template_name = 'book_reviews.html'
    context_object_name = 'reviews'
    paginate_by = 10

    def get_queryset(self):
        book_pk = self.kwargs.get('book_id')
        if book_pk is not None:
            book = Book.objects.get(pk=book_pk)
            queryset = BookReview.objects.filter(book=book).order_by('-id')
            return queryset

        return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        book_pk = self.kwargs.get('book_id')
        if book_pk is not None:
            book = Book.objects.get(pk=book_pk)
            context['book'] = book

        return context
