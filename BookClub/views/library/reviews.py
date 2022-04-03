"""Review related views."""
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView

from django.http import Http404,HttpResponseRedirect

from BookClub.forms import ReviewForm, BookReviewCommentForm
from BookClub.models import Book, BookReview, BookReviewComment

class CreateReviewView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Allow the user to create a review for a book."""
    template_name = 'reviews/create_review.html'
    model = BookReview
    form_class = ReviewForm
    redirect_location = 'book_reviews'

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super(LoginRequiredMixin, self).handle_no_permission()

        url = reverse('library_books')
        return redirect(url)

    def test_func(self):
        """Check if the user has already made a review for the given book."""
        try:
            book = Book.objects.get(pk=self.kwargs['book_id'])
            if BookReview.objects.filter(book=book, creator=self.request.user).exists():
                messages.info(self.request, f"You have already reviewed this book.")
                return False
            return True
        except Exception as e:
            messages.error(self.request, f"Error attempting to review book.")
            return False

    def form_valid(self, form):
        user = self.request.user
        book = Book.objects.get(pk=self.kwargs['book_id'])
        form.instance.creator = user
        form.instance.book = book
        response = super().form_valid(form)
        messages.success(self.request, f"You have created a review for '{book.title}'!")
        return response

    def form_invalid(self, form):
        messages.add_message(self.request, messages.ERROR, "The data provided was invalid!")
        return super().form_invalid(form)

    def get_success_url(self):
        """Return redirect URL after successful creation."""
        return reverse(self.redirect_location, kwargs={'book_id': self.kwargs['book_id']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['book'] = Book.objects.get(pk=self.kwargs['book_id'])
        return context


class EditReviewView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Allow a user to edit their own book review."""
    model = BookReview
    form_class = ReviewForm
    template_name = 'reviews/edit_review.html'
    context_object_name = 'book_review'
    # redirect_location = 'book_reviews'

    def test_func(self):
        """Check if the review exists."""
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
        return super().get_success_url()

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
    """Allow the user to delete their own book reviews."""

    def get_redirect_location(self):
        return reverse('book_reviews', kwargs=self.kwargs)

    def is_not_actionable(self):
        messages.error(self.request, "You are not allowed to delete this review or Review doesn\'t exist")

    def action(self, review):
        """Delete the review."""
        review.delete()
        messages.success(self.request, "You have deleted the review")

    def post(self, request, *args, **kwargs):
        """Get data for book, user and review.
        Try to delete review."""
        try:
            book = Book.objects.get(id=self.kwargs['book_id'])
            current_user = self.request.user
            review = BookReview.objects.get(book=book, creator=current_user)
            self.action(review)
            return redirect(self.get_redirect_location())

        except:
            self.is_not_actionable()
            return redirect(self.get_redirect_location())

    def get(self, request, *args, **kwargs):
        messages.error(self.request, "You are not allowed to delete this review or Review doesn\'t exist")
        return redirect(self.get_redirect_location())


class ReviewDetailView(ListView):
    """Render the details of a given review."""
    model = BookReviewComment
    paginate_by = 10
    template_name = 'reviews/review_details.html'
    context_object_name = 'comments'
    pk_url_kwarg = 'review_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['review_comment_form'] = BookReviewCommentForm()
        try:
            review = BookReview.objects.get(pk=self.kwargs.get('review_id'))
            context['review'] = review
        except:
            raise Http404("Given review id not found....")
        return context

    def get_queryset(self):
        try:
            review = BookReview.objects.get(pk=self.kwargs.get('review_id'))
            comments = review.get_comments()
        except:
            comments = []
        return comments


class CreateCommentForReviewView(LoginRequiredMixin, CreateView):
    """Allow the user to create a comment for a given review."""
    model = BookReviewComment
    form_class = BookReviewCommentForm
    http_method_names = ['post']

    def form_valid(self, form):
        try:
            review = BookReview.objects.get(pk=self.kwargs['review_id'])
            form.instance.creator = self.request.user
            form.instance.book_review = review
            self.object = form.save()
            return super().form_valid(form)
        except:
            messages.add_message(self.request, messages.ERROR,
                                 "There was an error making that comment, try again!")
            return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        messages.add_message(self.request, messages.ERROR,
                             "There was an error making that comment, try again!")
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('book_review', kwargs=self.kwargs)


class DeleteCommentForReviewView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Allow the user to delete their own comment from a review."""

    model = BookReviewComment
    http_method_names = ['post']
    pk_url_kwarg = 'comment_id'

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super(LoginRequiredMixin, self).handle_no_permission()
        else:
            return redirect(self.get_success_url())

    def test_func(self):
        """Check if the owner of the comment is the current user."""
        try:
            comment = BookReviewComment.objects.get(pk=self.kwargs['comment_id'])
            if comment.creator != self.request.user:
                messages.add_message(self.request, messages.ERROR, 'Access denied!')
                return False

            return True
        except:
            messages.add_message(self.request, messages.ERROR, 'The comment you tried to delete was not found!')
            return False

    def get_success_url(self):
        self.kwargs.pop('comment_id')
        return reverse('book_review', kwargs=self.kwargs)
