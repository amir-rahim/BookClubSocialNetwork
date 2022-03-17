"""Review Related Views"""
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View
from django.views.generic.edit import CreateView, UpdateView

from BookClub.forms.review import ReviewForm
from BookClub.helpers import delete_bookreview
from BookClub.models import Book, BookReview


class CreateReviewView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    template_name = 'create_review.html'
    model = BookReview
    form_class = ReviewForm
    redirect_location = 'book_reviews'

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super(LoginRequiredMixin, self).handle_no_permission()

        messages.error(self.request, f"Error attempting to review book.")
        url = reverse('library_books')
        return redirect(url)

    def test_func(self):
        try:
            book = Book.objects.get(pk=self.kwargs['book_id'])
            reviewed = BookReview.objects.filter(book=book, creator=self.request.user).exists()
            return not reviewed
        except Exception as e:
            return False

    def form_valid(self, form):
        user = self.request.user
        book = Book.objects.get(pk=self.kwargs['book_id'])
        form.instance.creator = user
        form.instance.book = book
        response = super().form_valid(form)
        messages.success(self.request, f"Successfully reviewed '{book.title}'!")
        return response

    def form_invalid(self, form):
        messages.add_message(self.request, messages.ERROR, "The data provided was invalid!")
        return super().form_invalid(form)

    def get_success_url(self):
        """Return redirect URL after successful creation."""
        messages.add_message(self.request, messages.SUCCESS, "You have created a book review!")
        return reverse(self.redirect_location, kwargs={'book_id': self.kwargs['book_id']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['book'] = Book.objects.get(pk=self.kwargs['book_id'])
        return context


class EditReviewView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = BookReview
    form_class = ReviewForm
    template_name = 'edit_review.html'
    context_object_name = 'book_review'
    redirect_location = 'book_reviews'

    def test_func(self):
        try:
            book = Book.objects.get(pk=self.kwargs['book_id'])
            book_review = BookReview.objects.get(book=book, creator=self.request.user)
            return True
        except Exception as e:
            messages.error(self.request, "Book or review not found!")
            return False

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super(LoginRequiredMixin, self).handle_no_permission()
        else:
            return redirect('book_reviews', self.kwargs['book_id'])

    def get_success_url(self):
        """Return redirect URL after successful update."""
        messages.add_message(self.request, messages.SUCCESS, "You have updated the book review!")
        return reverse(self.redirect_location, kwargs={'book_id': self.kwargs['book_id']})

    def get_object(self):
        book = Book.objects.get(pk=self.kwargs['book_id'])
        review = BookReview.objects.get(book=book, creator=self.request.user)
        return review

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        book_review = self.get_object()
        context['book_review'] = book_review
        context['id'] = book_review.id
        context['book'] = book_review.book
        return context


class DeleteReviewView(LoginRequiredMixin, View):
    redirect_location = 'library_books'  # Need to change to review list view or somewhere else

    """Handles no permssion and Reviews that don't exist"""

    def is_not_actionable(self):
        messages.error(self.request, "You are not allowed to delete this review or Review doesn\'t exist")

    def action(self, review):
        delete_bookreview(review)
        messages.success(self.request, "You have deleted the review")

    def post(self, request, *args, **kwargs):
        try:
            book = Book.objects.get(id=self.kwargs['book_id'])
            current_user = self.request.user
            review = BookReview.objects.get(book=book, creator=current_user)
            self.action(review)
            return redirect(self.redirect_location)

        except:
            self.is_not_actionable()
            return redirect(self.redirect_location)

    def get(self, request, *args, **kwargs):
        messages.error(self.request, "You are not allowed to delete this review or Review doesn\'t exist")
        return redirect(self.redirect_location)
