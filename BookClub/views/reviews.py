from BookClub.helpers import delete_bookreview
from BookClub.models import *
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic import View
from BookClub.models import *

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
