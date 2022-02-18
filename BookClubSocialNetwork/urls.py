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

# from BookClub.views.action_views import DemoteMemberView, PromoteView

urlpatterns = [
    # '''Core URLs'''
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),


    # '''Authentication URLs'''
    path('login/', views.LogInView.as_view(), name='login'),
    path('sign_up/', views.SignUpView.as_view(), name='sign_up'),
    path('log_out/', views.LogOutView.as_view(), name='log_out'),
    # '''User URLs'''
    path('user_dashboard/', views.UserDashboardView.as_view(), name='user_dashboard'),
    path('edit_profile/', views.EditProfileView.as_view(), name='edit_profile'),
    path('password_change/', views.ChangePasswordView.as_view(), name='password_change'),

    # '''Action URLs'''
    path('join_club/<str:club_url_name>/', views.JoinClubView.as_view(), name='join_club'),
    path('leave_club/<str:club_url_name>/', views.LeaveClubView.as_view(), name='leave_club'),
    path('promote_member/<str:club_url_name>/', views.PromoteMemberView.as_view(), name='promote_member'),
    path('demote_member/<str:club_url_name>/', views.DemoteMemberView.as_view(), name='demote_member'),
    path('transfer_ownership/<str:club_url_name>/', views.TransferOwnershipView.as_view(), name='transfer_ownership'),
    path('kick_member/<str:club_url_name>/', views.KickMemberView.as_view(), name='kick_member'),
    path('delete_club/<str:club_url_name>/',views.DeleteClubView.as_view(),name='delete_club'),

    # '''Membership URLs'''
    path('club/available_clubs/', views.AvailableClubsView.as_view(), name='available_clubs'),
    path('club/my_club_memberships/', views.MyClubMembershipsView.as_view(), name='my_club_memberships'),
    path('club/create_club/', views.clubs.CreateClubView.as_view(), name = 'create_club'),

    # '''Club URLs'''
    path('club/<str:club_url_name>/', views.ClubDashboardView.as_view(), name='club_dashboard'),
    path('club/<str:club_url_name>/members/', views.MembersListView.as_view(), name='member_list'),
    path('club/<str:club_url_name>/edit/', views.EditClubView.as_view(), name='edit_club'),

    # '''Meeting URLs'''
    path('club/<str:club_url_name>/meetings/create/', views.CreateMeetingView.as_view(), name ='create_meeting'),


]
