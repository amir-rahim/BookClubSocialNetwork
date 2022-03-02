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
from BookClub.forms.review import ReviewForm

class CreateReviewView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    template_name = 'create_review.html'
    model = BookReview
    form_class = ReviewForm
    success_url = reverse_lazy('home') # need to remove this attribute and amend 'get_absolute_url' method in BookReview model

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
        return currentUser == review.user

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
            review = BookReview.objects.get(book = book,user = currentUser)
           
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
