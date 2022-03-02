"""Forum Related Views"""
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView

from BookClub.forms.forum_forms import CreatePostForm
from BookClub.models import ForumPost, ForumComment, Forum, User, Club


class ForumPostView(DetailView):
    model = ForumPost
    paginate_by = 10
    template_name = 'forum_post.html'
    context_object_name = 'post'
    pk_url_kwarg = 'post_id'
    success_url = '/forum/'


class GlobalForumView(CreateView, ListView):
    model = ForumPost
    template_name = 'global_forum.html'
    context_object_name = 'posts'
    paginate_by = 10
    form_class = CreatePostForm
    success_url = "/forum/"

    def get_queryset(self):
        forum = Forum.objects.get(associatedWith=None)
        posts = forum.posts.all()
        return posts

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['forum'] = Forum.objects.get(associatedWith=None)
        replies = 0
        votes_cast = 0
        for post in context['forum'].posts.all():
            replies += post.comments.all().count()
            votes_cast = post.votes.all().count()
        context['replies'] = replies
        context['votes'] = votes_cast
        context['usercount'] = User.objects.all().count()
        return context

    def form_valid(self, form):
        if self.kwargs.get('club_url_name') is not None:
            """insert club code here"""
            club = Club.objects.get(
                club_url_name=self.kwargs.get('club_url_name'))
            forum = Forum.objects.get(associatedWith=club)
        else:
            forum = Forum.objects.get(associatedWith=None)

        form.instance.creator = self.request.user
        self.object = form.save()
        forum.add_post(self.object)
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.add_message(self.request, messages.ERROR,
                             "There was an error making that post, try again!")
        return super().form_invalid(form)
