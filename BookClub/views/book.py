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
            reviews = BookReview.objects.filter()
            if reviews:
                context['reviews'] = reviews    

        return context