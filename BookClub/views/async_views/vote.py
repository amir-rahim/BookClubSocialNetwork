from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.generic import CreateView

from BookClub.forms import VoteForm
from BookClub.models import Vote


class CreateVoteView(LoginRequiredMixin, CreateView):
    model = Vote
    http_method_names = ['post']
    form_class = VoteForm

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)

        if len(form.errors) == 1 and len(form.non_field_errors()) == 1:
            user = form.instance.creator
            content_type = form.instance.content_type
            object_id = form.instance.object_id
            this_vote_type = form.instance.type
            existing_vote = Vote.objects.filter(creator=user, content_type=content_type, object_id=object_id)

            if existing_vote.exists():
                existing_vote = existing_vote.get()
                existing_vote_type = existing_vote.type
                existing_vote.delete()
                if(this_vote_type == existing_vote_type):
                    return self.get_response_json(form, None)

        return super().post(request, *args, **kwargs)

    def get_response_json(self, form, vote):
        try:
            object_type = ContentType.objects.get(pk=form.instance.content_type.id)
            target = object_type.get_object_for_this_type(pk=form.instance.object_id)
            upvoted = False
            downvoted = False
            no_vote = True
            if vote is not None:
                no_vote = False
                if vote.type:
                    upvoted = True
                else:
                    downvoted = True
            response = JsonResponse(
                ({"rating": target.rating, "downvote": downvoted, "upvote": upvoted, "no_vote": no_vote}))
            return response
        except Exception:
            return redirect(self.get_success_url());

    def form_invalid(self, form):
        return self.get_response_json(form, None)

    def form_valid(self, form):
        super().form_valid(form)
        return self.get_response_json(form, self.object)

    def get_success_url(self):
        referer = self.request.headers['Referer']
        return referer
