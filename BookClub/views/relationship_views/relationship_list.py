"""Views related to user to user relationships."""
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from BookClub.models import User, UserToUserRelationship


class FollowerListView(LoginRequiredMixin, TemplateView):
    """Render the list of other users with a following
    or follower relationship with the current user."""
    model = User
    paginate_by = 20
    template_name = 'user/following_followers.html'

    def get_followers(self):
        if self.kwargs.get('username'):
            username = self.kwargs.get('username')
        else:
            username = self.request.user.username
        queryset = None
        user = User.objects.get(username=username)
        followers = user.user_relationships_target.all().order_by(
            '-created_on').values('source_user')
        queryset = User.objects.filter(pk__in=followers)
        return queryset

    def get_followees(self):
        if self.kwargs.get('username'):
            username = self.kwargs.get('username')
        else:
            username = self.request.user.username
        queryset = None
        user = User.objects.get(username=username)
        followees = user.user_relationships_source.all().order_by(
            '-created_on').values('target_user')
        queryset = User.objects.filter(pk__in=followees)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.kwargs.get('username'):
            username = self.kwargs.get('username')
            context['own'] = False
        else:
            username = self.request.user
            context['own'] = True
        user = User.objects.get(username=username)
        context['displayed_user'] = user
        context['username'] = username
        context['followers'] = self.get_followers()
        context['followees'] = self.get_followees()
        return context
