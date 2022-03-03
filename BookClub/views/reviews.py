'''Review Related Views'''
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic.edit import CreateView, UpdateView

from BookClub.forms.review import ReviewForm
from BookClub.helpers import delete_bookreview
from BookClub.models import *


class CreateReviewView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    template_name = 'create_review.html'
    model = BookReview
    form_class = ReviewForm
    redirect_location = 'book_reviews'  # need to remove this attribute and amend 'get_absolute_url' method in BookReview model

    def test_func(self):
        try:
            book = Book.objects.get(pk=self.kwargs['book_id'])
            reviewed = BookReview.objects.filter(book=book, user=self.request.user).exists()
            return not reviewed
        except:
            return False

    def form_valid(self, form):
        user = self.request.user
        book = Book.objects.get(pk=self.kwargs['book_id'])
        form.instance.user = user
        form.instance.book = book
        response = super().form_valid(form)
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
            book_review = BookReview.objects.get(book=book, user=self.request.user)
            if book_review.user == self.request.user:
                return True
            else:
                messages.error(self.request, 'You cannot edit this review!')
                return False
        except:
            messages.error(self.request, 'Book or review not found!')
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
        return BookReview.objects.get(book=book, user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        book_review = self.get_object()
        context['book_review'] = book_review
        context['id'] = book_review.id
        context['book'] = book_review.book
        return context


class DeleteReviewView(LoginRequiredMixin, View):
    redirect_location = 'library_books'  # Need to change to review list view or somewhere else
    """Checking whether the action is legal"""

    def is_actionable(self, currentUser, review):
        return currentUser == review.user

    """Handles no permssion and Reviews that don't exist"""

    def is_not_actionable(self):
        messages.error(self.request, "You are not allowed to delete this review or Review doesn\'t exist")

    def action(self, review):
        delete_bookreview(review)
        messages.success(self.request, "You have deleted the review")

    def post(self, request, *args, **kwargs):
        try:
            book = Book.objects.get(id=self.kwargs['book_id'])
            currentUser = self.request.user
            review = BookReview.objects.get(book=book, user=currentUser)

            if self.is_actionable(currentUser, review):
                self.action(review)
                return redirect(self.redirect_location)
            else:
                self.is_not_actionable()
        except:
            self.is_not_actionable()
            return redirect(self.redirect_location)

    """Should look the same as post but will not do anything"""

    def get(self, request, *args, **kwargs):
        messages.error(self.request, "You are not allowed to delete this review or Review doesn\'t exist")
        return redirect(self.redirect_location)
