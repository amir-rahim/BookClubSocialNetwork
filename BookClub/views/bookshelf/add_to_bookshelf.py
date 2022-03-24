"""Add to Bookshelf Related Views"""
from django.contrib import messages
from django.views.generic import View
from django.shortcuts import redirect, reverse
from django.contrib.auth.mixins import LoginRequiredMixin

from BookClub.models import BookShelf, Book


class AddToBookShelfView(LoginRequiredMixin, View):

    redirect_url = 'library_books'
    
    def get(self, request, *args, **kwargs):
        return redirect(self.redirect_url)

    def is_actionable(self, book, status):
        """Check if user can remove a book"""

        return (not BookShelf.objects.filter(user=self.request.user, book=book).exists()) and int(status) <= 3 and int(status) >= 0

    def is_not_actionable(self):
        """If user cannot remove book"""

        return messages.error(self.request, "You cannot add that book!")

    def action(self, book, status):
        """User removes the book"""
        
        entry = BookShelf.objects.create(user=self.request.user, book=book, status=status)
        entry.save()
        messages.success(self.request, "You have added the book to your bookshelf.")

    def post(self, *args, **kwargs):

        try:
            status = self.request.POST.get('status')
            book = Book.objects.get(id=self.kwargs['book_id'])
        except:
            messages.error(self.request, "Error, book or bookshelf not found.")
            return redirect(self.redirect_url)

        if self.is_actionable(book, status):
            self.action(book, status)
        else:
            self.is_not_actionable()

        return redirect('book_view', book_id=self.kwargs['book_id'])
