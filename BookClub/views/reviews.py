'''Review Related Views'''
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic.edit import CreateView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse

from BookClub.models import User, Book, BookReview
from BookClub.forms.review import ReviewForm

class CreateReviewView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    template_name = 'create_review.html'
    model = BookReview
    form_class = ReviewForm
    success_url = reverse_lazy('home') # need to remove this attribute and amend 'get_absolute_url' method in BookReview model

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super(LoginRequiredMixin, self).handle_no_permission()
        else:
            messages.error(self.request, f"Error attempting to review book.")
            url = reverse('library_books')
            return redirect(url)

    def test_func(self):
        try:
            book = Book.objects.get(pk = self.kwargs['book_id'])
            reviewed = BookReview.objects.filter(book = book, user = self.request.user).exists()
            return not reviewed
        except:
            return False

    def form_valid(self, form):
        user = self.request.user
        book = Book.objects.get(pk = self.kwargs['book_id'])
        form.instance.user = user
        form.instance.book = book
        response = super().form_valid(form)
        messages.success(self.request, f"Successfully reviewed '{book.title}'!")
        return response

    def form_invalid(self, form):
        messages.add_message(self.request, messages.ERROR, "The data provided was invalid!")
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['book'] = Book.objects.get(pk = self.kwargs['book_id'])
        return context
