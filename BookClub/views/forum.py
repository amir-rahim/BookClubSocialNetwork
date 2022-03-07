"""Forum Related Views"""
from attr import assoc
from django.contrib import messages
from django.urls import reverse
from django.views.generic import ListView, DetailView, CreateView
from django.views.generic.edit import UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from BookClub.forms.forum_forms import CreateForumCommentForm, CreatePostForm
from BookClub.helpers import has_membership
from BookClub.models import ForumPost, ForumComment, Forum, User, Club
from BookClub.models.club_membership import ClubMembership
from django.contrib.contenttypes.models import ContentType

class ClubMemberTestMixin(UserPassesTestMixin):
    
    def test_func(self):
        if self.kwargs.get('club_url_name') is not None:
            club = Club.objects.get(
                club_url_name=self.kwargs.get('club_url_name'))
            return has_membership(club=club, user=self.request.user)
        else:
            return True
        

class ForumPostView(ClubMemberTestMixin, DetailView):
    model = ForumPost
    paginate_by = 10
    template_name = 'forum_post.html'
    context_object_name = 'post'
    pk_url_kwarg = 'post_id'
    success_url = '/forum/'


class ForumView(ClubMemberTestMixin, ListView):
    model = ForumPost
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        if self.kwargs.get('club_url_name') is not None:
            club = Club.objects.get(club_url_name=self.kwargs.get('club_url_name'))
            forum = Forum.objects.get(associatedWith=club)
        else:
            forum = Forum.objects.get(associatedWith=None)
        posts = forum.posts.all()
        return posts

    def get_template_names(self):
        #if self.kwargs.get('club_url_name') is not None:
         #   names = ['club_forum.html']
         #   return names
        #else:
            names = ['global_forum.html']
            return names
    
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if self.kwargs.get('club_url_name') is not None:
            club = Club.objects.get(club_url_name=self.kwargs.get('club_url_name'))
            context['club'] = club
            context['forum'] = Forum.objects.get(associatedWith=club)
            context['usercount'] = ClubMembership.objects.filter(club=club).count()
        else:
            context['forum'] = Forum.objects.get(associatedWith=None)
            context['usercount'] = User.objects.all().count()
            
        replies = 0
        votes_cast = 0
        
        for post in context['forum'].posts.all():
            replies += post.comments.all().count()
            votes_cast = post.votes.all().count()
            
        context['replies'] = replies
        context['votes'] = votes_cast
         
        return context
    

class CreatePostView(LoginRequiredMixin, ClubMemberTestMixin, CreateView):
    form_class = CreatePostForm
    model = ForumPost
    success_url = None
    http_method_names = ['post']
    
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
    
    def get_success_url(self):
        if self.kwargs.get('club_url_name') is not None:
            pass
            #placeholder till club forums is set up
        else:
            return reverse('global_forum')
    

class CreateCommentView(LoginRequiredMixin, ClubMemberTestMixin, CreateView):
    model = ForumComment
    form_class = CreateForumCommentForm
    http_method_names = ['post']
    
    def form_valid(self, form):
        if self.kwargs.get('post_id') is not None:
            form.instance.creator = self.request.user
            self.object = form.save()
            post = ForumPost.objects.get(pk=self.kwargs['post_id'])
            post.add_comment(self.object)
            return super().form_valid(form)
        else:
            return self.form_invalid(self)
    
    def form_invalid(self, form):
        messages.add_message(self.request, messages.ERROR,
                             "There was an error making that comment, try again!")
        return super().form_invalid(form)

    def get_success_url(self):
        if self.kwargs.get('club_url_name') is not None:
            pass
            #placeholder till club forums is set up
        else:
            return reverse('forum_post', kwargs = self.kwargs)


class EditForumPostView(LoginRequiredMixin, ClubMemberTestMixin, UpdateView):
    model = ForumPost
    form_class = CreateForumCommentForm
    template_name = 'edit_forum_post.html'
    pk_url_kwarg = 'post_id'
    context_object_name = 'post'
    
    def get_success_url(self):
        return reverse('forum_post', kwargs=self.kwargs)
    
class DeleteForumPostView(LoginRequiredMixin, ClubMemberTestMixin, DeleteView):
    model = ForumPost
    http_method_names = ['post']
    pk_url_kwarg = 'post_id'
    
    def get_success_url(self):
        self.kwargs.pop('post_id')
        if self.kwargs.get('club_url_name') is not None:
            pass
            #placeholder till club forums is set up
        else:
            return reverse('global_forum', kwargs=self.kwargs)
