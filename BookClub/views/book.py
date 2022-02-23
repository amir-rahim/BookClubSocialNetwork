from numpy import average
from BookClub.models import Book, BookReview
from django.views.generic import DetailView

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
                context['reviews'] = reviews
                sum = 0
                for review in reviews:
                    sum += review.rating
                avg = sum/len(reviews)
                context['average'] = avg
            else:
                reviews = None
        return context