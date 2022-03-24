from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from BookClub.models import User, UserToUserRelationship


class FollowerListView(LoginRequiredMixin, TemplateView):
    model = User
    paginate_by = 20
    template_name = 'following_followers.html'

    def get_followers(self):
        user = self.kwargs.get('username')
        queryset = None
        user = User.objects.get(username=user)
        followers = user.user_relationships_target.all().order_by(
            '-created_on').values('source_user')
        queryset = User.objects.filter(pk__in=followers)
        return queryset

    def get_followees(self):
        user = self.kwargs.get('username')
        queryset = None
        user = User.objects.get(username=user)
        followees = user.user_relationships_source.all().order_by(
            '-created_on').values('target_user')
        queryset = User.objects.filter(pk__in=followees)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['displayed_user'] = User.objects.get(
            username=self.kwargs.get('username'))
        context['followers'] = self.get_followers()
        context['followees'] = self.get_followees()
        return context
