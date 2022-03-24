from django.http import HttpResponse, JsonResponse
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.mixins import LoginRequiredMixin

from BookClub.models import User, UserToUserRelationship


class FollowUserView(LoginRequiredMixin, View):

    def get_record_status(self):
        source_user = self.request.user
        target_user = get_object_or_404(User, username=self.kwargs['username'])
        relationship_exists = UserToUserRelationship.objects.filter(source_user=source_user, target_user=target_user).exists()
        response = {
            'target_user_username': target_user.username,
            'is_followed': relationship_exists,
        }
        return JsonResponse(response)

    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            return self.get_record_status()

        return redirect('user_profile', username=self.kwargs['username'])

    def post(self, request, *args, **kwargs):
        if request.is_ajax():
            source_user = self.request.user
            target_user = get_object_or_404(User, username=self.kwargs['username'])
            try:
                relationship_record = UserToUserRelationship.objects.get(source_user=source_user, target_user=target_user)
                relationship_record.delete()
            except ObjectDoesNotExist:
                UserToUserRelationship.objects.create(
                    source_user=source_user,
                    target_user=target_user,
                    relationship_type=UserToUserRelationship.UToURelationshipTypes.FOLLOWING
                )
            return self.get_record_status()

        return redirect('user_profile', username=self.kwargs['username'])
