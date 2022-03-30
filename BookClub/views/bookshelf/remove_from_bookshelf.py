"""View for removing a book from bookshelf."""
from django.contrib import messages
from django.views.generic import View
from django.shortcuts import redirect, reverse
from django.contrib.auth.mixins import LoginRequiredMixin

from BookClub.models import BookShelf, Book


class RemoveFromBookShelfView(LoginRequiredMixin, View):
    """Allow the user to remove a book from their bookshelf."""

    redirect_url = 'bookshelf'
    
    def get(self, request, *args, **kwargs):
        return redirect(self.redirect_url)

    def is_actionable(self, book):
        """Check if user can remove the book."""

        return BookShelf.objects.filter(user=self.request.user, book=book).exists()

    def is_not_actionable(self):
        """Throw error message if book cannot be removed."""

        return messages.error(self.request, "You cannot remove that book!")

    def action(self, book):
        """Remove book from the user's bookshelf."""
        
        entry = BookShelf.objects.get(user=self.request.user, book=book)
        entry.delete()
        messages.success(self.request, "You have removed this book from your bookshelf.")

    def post(self, *args, **kwargs):
        """Get book and try to remove it from the user's bookshelf."""
        try:
            book = Book.objects.get(id=self.kwargs['book_id'])
        except:
            messages.error(self.request, "Error, book or bookshelf not found.")
            return redirect(self.redirect_url)

        if self.is_actionable(book):
            self.action(book)
        else:
            self.is_not_actionable()

        return redirect(self.redirect_url)
