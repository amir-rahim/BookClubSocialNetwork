from email.headerregistry import ContentDispositionHeader
from django.shortcuts import redirect
from django.urls import reverse
from BookClub.forms import VoteForm
from BookClub.models import Vote, RatedContent
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView
from django.contrib import messages

class CreateVoteView(LoginRequiredMixin, CreateView):
    model = Vote
    http_method_names = ['post']
    form_class = VoteForm
    
    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if not form.is_valid():
            print(form.errors)
            if len(form.errors) == 1 and len(form.non_field_errors())== 1:
                user = self.request.user
                content_type = form.instance.content_type
                object_id = form.instance.object_id
                thisVoteType = form.instance.type
                
                previousVote = Vote.objects.get(
                    creator=user, content_type=content_type, object_id=object_id)
                previousVoteType = previousVote.type
                
                if(previousVoteType != thisVoteType):
                    previousVote.delete()
                    
                    
        return super().post(request, *args, **kwargs)
    
    def form_invalid(self, form):
        messages.error(self.request, "Error making that vote")
        return redirect(self.get_success_url())
    
    def get_success_url(self):
        referer = self.request.headers['Referer']
        return referer
