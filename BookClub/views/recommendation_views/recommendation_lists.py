from django.http import JsonResponse
from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.template.loader import render_to_string
from BookClub.helpers import get_club_from_url_name
from BookClub.models import UserRecommendations, ClubRecommendations, User, Club, Book
from RecommenderModule.recommendations_provider import get_club_personalised_recommendations, get_club_popularity_recommendations, get_user_personalised_recommendations, get_user_popularity_recommendations


class RecommendationBaseView(LoginRequiredMixin, TemplateView):
    model = Book
    template_name = "recommendations/recommendation_base.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.kwargs.get('club_url_name'):
            club = get_club_from_url_name(self.kwargs.get('club_url_name'))
            context['current_club'] = club
        return context
    
    def get_template_names(self):
        club = self.kwargs.get('club_url_name')
        if club is not None:
            return "recommendations/recommendation_base_club.html"
        return "recommendations/recommendation_base_user.html"
    

class RecommendationUserListView(LoginRequiredMixin, TemplateView):
    model = Book
    template_name = "partials/recommendation_list_view.html"
    context_object_name = "recommendations"

    def get_queryset(self):
        user = self.request.user
        recommendations = UserRecommendations.objects.get_or_create(user=user)[0]
        if recommendations.modified:
            isbns = get_user_personalised_recommendations(
                self.request.user.username)
            if len(isbns) < 3:
                isbns = get_user_popularity_recommendations(
                    self.request.user.username)
            recommendations.recommendations = isbns
            recommendations.modified = False
            recommendations.save()
        else:
            isbns = recommendations.recommendations
        books = Book.objects.filter(ISBN__in=isbns)
        return books
    
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        recommendations = self.get_queryset()
        context['recommendations'] = recommendations
        html = render_to_string(template_name=self.template_name, context=context, request=request)
        data_dict = {"html_from_view" : html}
        return JsonResponse(data=data_dict, safe=False)
    
class RecommendationClubListView(LoginRequiredMixin, TemplateView):
    model = Book
    template_name = "partials/recommendation_list_view.html"
    context_object_name = "recommendations"
    
    def get_queryset(self):
        club = Club.objects.get(club_url_name=self.kwargs.get('club_url_name'))
        recommendations = ClubRecommendations.objects.get_or_create(club=club)[0]
        if recommendations.modified:
            isbns = get_user_personalised_recommendations(
                self.request.user.username)
            if len(isbns) < 3:
                isbns = get_user_popularity_recommendations(
                    self.request.user.username)

            recommendations.recommendations = isbns
            recommendations.modified = False
            recommendations.save()
        else:
            isbns = recommendations.recommendations
        books = Book.objects.filter(ISBN__in=isbns)
        return books
    
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        recommendations = self.get_queryset()
        context['recommendations'] = recommendations
        html = render_to_string(
            template_name=self.template_name, context=context, request=request)
        data_dict = {"html_from_view": html}
        return JsonResponse(data=data_dict, safe=False)

    