"""Update Bookshelf Related Views"""
from django.contrib import messages
from django.views.generic import View
from django.shortcuts import redirect, reverse
from django.contrib.auth.mixins import LoginRequiredMixin

from BookClub.models import BookShelf, Book


class UpdateBookShelfView(LoginRequiredMixin, View):
    """View for updating books in the book shelf."""

    redirect_url = 'bookshelf'
    
    def get(self, request, *args, **kwargs):
        return redirect(self.redirect_url)

    def is_actionable(self, book, status):
        """Check if user can update status (move book)"""

        return BookShelf.objects.filter(user=self.request.user, book=book).exists() and int(status) <= 3 and int(status) >= 0

    def is_not_actionable(self):
        """If user cannot update status (move book)"""

        return messages.error(self.request, "You cannot move that book!")

    def action(self, book, status):
        """Update the book's status"""
        
        entry = BookShelf.objects.get(user=self.request.user, book=book)
        entry.delete()
        entry = BookShelf.objects.create(user=self.request.user, book=book, status=status)
        entry.save()
        messages.success(self.request, "You have moved this book.")

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

        return redirect(self.redirect_url)
