"""Review list related views."""
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse
from django.views.generic import ListView

from BookClub.models import User, Club, BookReview


class CommunityReviewFeedView(LoginRequiredMixin, ListView):
    """Renders the list of community reviews feed."""
    model = BookReview
    paginate_by = 10
    context_object_name = 'reviews'
    template_name = 'reviews/review_feed.html'

    def get_queryset(self):
        reviews = BookReview.objects.all()
        return reviews

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_user'] = None

        return context


class PersonalReviewFeedView(LoginRequiredMixin, ListView):
    """Renders the list of reviews made by the user."""
    model = BookReview
    paginate_by = 10
    context_object_name = 'reviews'
    template_name = 'reviews/review_feed.html'

    def get_queryset(self):
        reviews = BookReview.objects.filter(creator=self.request.user)
        return reviews

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_user'] = self.request.user

        return context
