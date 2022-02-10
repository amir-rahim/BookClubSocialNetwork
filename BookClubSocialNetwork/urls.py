"""BookClubSocialNetwork URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from BookClub import views
from BookClub.views.action_views import DemoteMemberView, PromoteView

urlpatterns = [
    # '''Core URLs'''
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),

    # '''Authentication URLs'''
    path('login/', views.LogInView.as_view(), name='login'),
    path('sign_up/', views.SignUpView.as_view(), name='sign_up'),
    path('log_out/', views.LogOutView.as_view(), name='log_out'),

  
    path('available_clubs/', views.AvailableClubsView.as_view(), name='available_clubs'),
    path('my_club_memberships/', views.MyClubMembershipsView.as_view(), name='my_club_memberships'),


    # '''Club URLs'''
    path('club_dashboard/', views.club_dashboard, name='club_dashboard'),
    path('create_club/', views.clubs.CreateClubView.as_view(), name = 'create_club'),

    #'''Action URLS (temp)'''
    path('promote_member/<int:clubid>/<int:user_id>',views.PromoteView.as_view(),name='promote'),
    path('demote_member/<int:clubid>/<int:user_id>',views.DemoteMemberView.as_view(),name='demote')
    ]

