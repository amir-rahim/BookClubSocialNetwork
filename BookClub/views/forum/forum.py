"""Forum related views."""
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import ListView, CreateView
from django.views.generic.edit import UpdateView, DeleteView

from BookClub.forms.forum_forms import CreateForumCommentForm, CreatePostForm
from BookClub.helpers import get_club_from_url_name, has_membership
from BookClub.models import ForumPost, ForumComment, Forum, User, Club, ClubMembership
from BookClub.authentication_mixins import ClubMemberTestMixin


class ForumPostView(ClubMemberTestMixin, ListView):
    """Render a single forum post."""
    model = ForumComment
    paginate_by = 10
    template_name = 'forum/forum_post.html'
    context_object_name = 'comments'
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.kwargs.get('club_url_name'):
            try:
                context['post'] = ForumPost.objects.get(pk=self.kwargs.get('post_id'))
                context['club'] = Club.objects.get(club_url_name=self.kwargs.get('club_url_name'))
            except ObjectDoesNotExist:
                raise Http404("Given club or post id not found....")
        else:
            try:
                context['post'] = ForumPost.objects.get(pk=self.kwargs.get('post_id'))
                context['club'] = None
            except ObjectDoesNotExist:
                raise Http404("Given club or post id not found....")
        return context

    def get_queryset(self):
        try:
            post = ForumPost.objects.get(pk=self.kwargs.get('post_id'))
            comments = post.get_comments()
        except ObjectDoesNotExist:
            comments = []
        return comments


class ForumView(ClubMemberTestMixin, ListView):
    """Render a list of forum posts."""
    model = ForumPost
    context_object_name = 'posts'
    paginate_by = 5
    template_name = 'forum/forums.html'

    def get_queryset(self):
        """Check if the current forums is associated with a club."""
        if self.kwargs.get('club_url_name') is not None:
            club = get_club_from_url_name(self.kwargs.get('club_url_name'))
            forum = Forum.objects.get(associated_with=club)
        else:
            forum = Forum.objects.get(associated_with=None)
        posts = forum.get_posts()
        return posts

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.kwargs.get('club_url_name') is not None:
            club = get_club_from_url_name(self.kwargs.get('club_url_name'))
            context['club'] = club
            context['forum'] = Forum.objects.get(associated_with=club)
            context['usercount'] = ClubMembership.objects.filter(club=club).count()
        else:
            context['club'] = None
            context['forum'] = Forum.objects.get(associated_with=None)
            context['usercount'] = User.objects.all().count()

        replies = 0
        votes_cast = 0

        for post in context['forum'].get_posts():
            replies += post.get_comments().count()
            votes_cast = post.votes.all().count()

        context['replies'] = replies
        context['votes'] = votes_cast

        return context


class CreatePostView(LoginRequiredMixin, ClubMemberTestMixin, CreateView):
    """Allow the user to create a post in forums."""
    form_class = CreatePostForm
    model = ForumPost
    success_url = None
    http_method_names = ['post']

    def form_valid(self, form):
        """If forums is associated to a club, check if the current user is a member before saving form."""
        if self.kwargs.get('club_url_name') is not None:
            club = get_club_from_url_name(self.kwargs.get('club_url_name'))
            forum = Forum.objects.get(associated_with=club)
        else:
            forum = Forum.objects.get(associated_with=None)

        form.instance.creator = self.request.user
        form.instance.forum = forum
        self.object = form.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.add_message(self.request, messages.ERROR,
                             "There was an error making that post, try again!")
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        if self.kwargs.get('club_url_name') is not None:
            return reverse('club_forum', kwargs=self.kwargs)
        else:
            return reverse('global_forum', kwargs=self.kwargs)


class CreateCommentView(LoginRequiredMixin, ClubMemberTestMixin, CreateView):
    """Allow the user to create comments."""
    model = ForumComment
    form_class = CreateForumCommentForm
    http_method_names = ['post']

    def form_valid(self, form):
        try:
            post = ForumPost.objects.get(pk=self.kwargs['post_id'])
            form.instance.creator = self.request.user
            form.instance.post = post
            self.object = form.save()
            return super().form_valid(form)
        except:
            messages.add_message(self.request, messages.ERROR,
                                 "There was an error making that comment, try again!")
            return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        messages.add_message(self.request, messages.ERROR,
                             "There was an error making that comment, try again!")
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('forum_post', kwargs=self.kwargs)


class EditForumPostView(LoginRequiredMixin, ClubMemberTestMixin, UpdateView):
    """Allow the user to edit a forum post."""
    model = ForumPost
    form_class = CreateForumCommentForm
    template_name = 'forum/edit_forum_post.html'
    pk_url_kwarg = 'post_id'
    context_object_name = 'post'

    def handle_no_permission(self):
        """If the forum is associated to a club, check if the user is a member."""
        if not self.request.user.is_authenticated:
            return super(LoginRequiredMixin, self).handle_no_permission()
        elif self.kwargs.get('club_url_name') is not None:
            club = get_club_from_url_name(self.kwargs.get('club_url_name'))
            membership = ClubMembership.objects.filter(user=self.request.user, club=club)
            if membership.count() != 1:
                return super(ClubMemberTestMixin, self).handle_no_permission()
            else:
                url = reverse('club_forum', kwargs={'club_url_name': self.kwargs['club_url_name']})
                return redirect(url)
        else:
            url = reverse('global_forum')
            return redirect(url)

    def test_func(self):
        try:
            post = ForumPost.objects.get(pk=self.kwargs['post_id'])
            if post.creator != self.request.user:
                messages.add_message(self.request, messages.ERROR, 'Access denied!')
                return False
            else:
                return True
        except:
            messages.add_message(self.request, messages.ERROR, 'The post you tried to edit was not found!')
            return False

    def get_success_url(self):
        return reverse('forum_post', kwargs=self.kwargs)


class DeleteForumPostView(LoginRequiredMixin, ClubMemberTestMixin, DeleteView):
    """Allow the user to delete their own posts."""
    model = ForumPost
    http_method_names = ['post']
    pk_url_kwarg = 'post_id'

    def handle_no_permission(self):
        """If the forums is associated to a club, check the user is a member."""
        self.kwargs.pop('comment_id', None)
        if not self.request.user.is_authenticated:
            return super(LoginRequiredMixin, self).handle_no_permission()
        elif self.kwargs.get('club_url_name') is not None:
            club = Club.objects.get(club_url_name=self.kwargs.get('club_url_name'))
            membership = ClubMembership.objects.filter(user=self.request.user, club=club)
            url = reverse('club_dashboard', kwargs={'club_url_name': self.kwargs['club_url_name']})
            return redirect(url)
        else:
            url = reverse('global_forum')
            return redirect(url)

    def test_func(self):
        """Only allow the owner of the post to delete it."""
        try:
            post = ForumPost.objects.get(pk=self.kwargs['post_id'])
            if post.creator != self.request.user:
                messages.add_message(self.request, messages.ERROR, 'Access denied!')
                return False

            return True
        except:
            messages.add_message(self.request, messages.ERROR, 'The post you tried to delete was not found!')
            return False

    def get_success_url(self):
        forum_club = ForumPost.objects.get(pk=self.kwargs['post_id']).forum.associated_with
        if forum_club is not None:
            return reverse('club_forum', kwargs={'club_url_name': forum_club.club_url_name})
        else:
            self.kwargs.pop('post_id')
            return reverse('global_forum', kwargs=self.kwargs)


class DeleteForumCommentView(LoginRequiredMixin, ClubMemberTestMixin, DeleteView):
    """Allow the user to delete their comments."""
    model = ForumComment
    http_method_names = ['post']
    pk_url_kwarg = 'comment_id'

    def handle_no_permission(self):
        """If the forums is associated to a club, check the user is a member."""
        self.kwargs.pop('comment_id', None)
        if not self.request.user.is_authenticated:
            return super(LoginRequiredMixin, self).handle_no_permission()
        elif self.kwargs.get('club_url_name') is not None:
            club = Club.objects.get(club_url_name=self.kwargs.get('club_url_name'))
            membership = ClubMembership.objects.filter(user=self.request.user, club=club)
            url = reverse('forum_post', kwargs=self.kwargs)
            return redirect(url)
        else:
            url = reverse('forum_post', kwargs=self.kwargs)
            return redirect(url)

    def test_func(self):
        """Only allow the creator of a comment to delete it."""
        try:
            comment = ForumComment.objects.get(pk=self.kwargs['comment_id'])
            if comment.creator != self.request.user:
                messages.add_message(self.request, messages.ERROR, 'Access denied!')
                return False

            return True
        except:
            messages.add_message(self.request, messages.ERROR, 'The comment you tried to delete was not found!')
            return False

    def get_success_url(self):
        self.kwargs.pop('comment_id')
        return reverse('forum_post', kwargs=self.kwargs)
