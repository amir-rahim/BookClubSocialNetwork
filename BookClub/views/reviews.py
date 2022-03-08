'''Review Related Views'''
from BookClub.helpers import delete_bookreview
from BookClub.models import *
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.generic import View
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy

from BookClub.models import *
from BookClub.models.review import *
from BookClub.forms.review import ReviewForm, BookReviewCommentForm

class CreateReviewView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    template_name = 'create_review.html'
    model = BookReview
    form_class = ReviewForm
    success_url = reverse_lazy('home') # need to remove this attribute and amend 'get_absolute_url' method in BookReview model

    def test_func(self):
        try:
            book = Book.objects.get(pk = self.kwargs['book_id'])
            reviewed = BookReview.objects.filter(book = book, creator = self.request.user).exists()
            can_see = not reviewed
            return can_see
            # return not reviewed
        except:
            return False

    def form_valid(self, form):
        user = self.request.user
        book = Book.objects.get(pk = self.kwargs['book_id'])
        form.instance.creator = user
        form.instance.book = book
        response = super().form_valid(form)
        messages.success(self.request, (f"Successfully reviewed '{book.title}'!"))
        return response

    def form_invalid(self, form):
        messages.add_message(self.request, messages.ERROR, "The data provided was invalid!")
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['book'] = Book.objects.get(pk = self.kwargs['book_id'])
        return context


class DeleteReviewView(LoginRequiredMixin,View):
    redirect_location = 'home' #Need to change to review list view or somewhere else
    """Checking whether the action is legal"""
    def is_actionable(self,currentUser,review):
        return currentUser == review.creator

    """Handles no permssion and Reviews that don't exist"""
    def is_not_actionable(self):
        messages.error(self.request,"You are not allowed to delete this review or Review doesn\'t exist")

    def action(self,currentUser,review):
        delete_bookreview(review)
        messages.success(self.request,"You have deleted the review")

    def post(self, request, *args, **kwargs):
        try:
            book = Book.objects.get(id = self.kwargs['book_id'])
            currentUser = self.request.user
            review = BookReview.objects.get(book = book,creator = currentUser)

            if self.is_actionable(currentUser,review):
                self.action(currentUser,review)
                return redirect(self.redirect_location)
            else:
                self.is_not_actionable()
        except:
            self.is_not_actionable()
            return redirect(self.redirect_location)

    """Should look the same as post but will not do anything"""
    def get(self, request, *args, **kwargs):
        return redirect(self.redirect_location)


class CreateCommentForReviewView(LoginRequiredMixin, View):
    http_method_names = ['post']

    def http_method_not_allowed(self, request, *args, **kwargs):
        messages.add_message(self.request, messages.ERROR, "Non-existing page was requested, so we redirected you here...")
        return redirect('book_view', book_id = self.kwargs['book_id']) # need to redirect to Review Detail view

    def post(self, *args, **kwargs):
        user = self.request.user
        form = BookReviewCommentForm(self.request.POST)
        try:
            review = BookReview.objects.get(pk = self.kwargs['book_review_id'])
            form.instance.bookReview = review
            if form.is_valid():
                form.save()
                messages.success(self.request, "You have commented on the review")
                return redirect('book_view', username = self.kwargs['username'])
            else:
                messages.add_message(self.request, messages.ERROR, "Your comment input was invalid...")
                for field in form.errors:
                    for error in form.errors[field]:
                        messages.add_message(self.request, messages.ERROR, form.fields[field].label + ' - ' + error)
                return redirect('book_view', username = self.kwargs['username'])

        except ObjectDoesNotExist:
            messages.add_message(self.request, messages.ERROR, "Non-existing list was targeted")
            return redirect('book_view', username = self.kwargs['username'])
