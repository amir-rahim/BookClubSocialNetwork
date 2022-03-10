from django.http import JsonResponse
from django.shortcuts import redirect
from BookClub.forms import VoteForm
from BookClub.models import Vote
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType

class CreateVoteView(LoginRequiredMixin, CreateView):
    model = Vote
    http_method_names = ['post']
    form_class = VoteForm
    
    def post(self, request, *args, **kwargs):
        form = self.get_form()
        
        if not form.is_valid():
            if len(form.errors) == 1 and len(form.non_field_errors())== 1:
                user = form.instance.creator
                content_type = form.instance.content_type
                object_id = form.instance.object_id
                thisVoteType = form.instance.type
                
                previousVote = Vote.objects.get(
                    creator=user, content_type=content_type, object_id=object_id)
                previousVoteType = previousVote.type
                
                if(previousVoteType != thisVoteType):
                    previousVote.delete()
                
                else:
                    self.form_invalid(form);
                    
                    
        return super().post(request, *args, **kwargs)
    
    def get_response_json(self, form, vote):
        try:
            object_type = ContentType.objects.get(pk=form.instance.content_type.id)
            object = object_type.get_object_for_this_type(pk=form.instance.object_id)
            upvoteUsable = True
            downvoteUsable = True
            if vote is not None:
                if vote.type:
                    upvoteUsable = False
                else:
                    downvoteUsable = False
            response = JsonResponse(({"rating": object.rating, "downvote": downvoteUsable, "upvote" : upvoteUsable}))
            return response
        except Exception:
            return self.get_failure_url();
    
    def form_invalid(self, form):
        return self.get_response_json(form, None)
    
    def form_valid(self, form):
        super().form_valid(form)
        return self.get_response_json(form, self.object)
    
    def get_failure_url(self):
        referer = self.request.headers['Referer']
        return referer
    
    def get_success_url(self):
        referer = self.request.headers['Referer']
        return referer
