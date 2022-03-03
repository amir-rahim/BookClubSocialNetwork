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
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView

urlpatterns = [
    # '''Core URLs'''
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('favicon.ico'))),

    # '''Authentication URLs'''
    path('login/', views.LogInView.as_view(), name='login'),
    path('sign_up/', views.SignUpView.as_view(), name='sign_up'),
    path('log_out/', views.LogOutView.as_view(), name='log_out'),

    # '''User URLs'''
    path('user/', views.UserDashboardView.as_view(), name='user_dashboard'),
    path('edit_profile/', views.EditProfileView.as_view(), name='edit_profile'),
    path('password_change/', views.ChangePasswordView.as_view(), name='password_change'),

    # '''User Profile URLs'''
    path('profile/<str:username>/', views.UserProfileView.as_view(), name='user_profile'),
    path('profile/<str:username>/memberships/', views.UserProfileMembershipsView.as_view(), name='user_memberships'),
    path('profile/<str:username>/following/', views.UserProfileFollowingView.as_view(), name='user_following'),

    # '''Action URLs'''
    path('join_club/<str:club_url_name>/', views.JoinClubView.as_view(), name='join_club'),
    path('leave_club/<str:club_url_name>/', views.LeaveClubView.as_view(), name='leave_club'),
    path('promote_member/<str:club_url_name>/', views.PromoteMemberView.as_view(), name='promote_member'),
    path('demote_member/<str:club_url_name>/', views.DemoteMemberView.as_view(), name='demote_member'),
    path('approve_applicant/<str:club_url_name>/', views.ApproveApplicantView.as_view(), name='approve_applicant'),
    path('reject_applicant/<str:club_url_name>/', views.RejectApplicantView.as_view(), name='reject_applicant'),

    path('transfer_ownership/<str:club_url_name>/', views.TransferOwnershipView.as_view(), name='transfer_ownership'),
    path('kick_member/<str:club_url_name>/', views.KickMemberView.as_view(), name='kick_member'),
    path('delete_club/<str:club_url_name>/', views.DeleteClubView.as_view(), name='delete_club'),

    # '''Membership URLs'''
    path('club/', views.AvailableClubsView.as_view(), name='available_clubs'),
    path('memberships/', views.MyClubMembershipsView.as_view(), name='my_club_memberships'),
    path('create/', views.clubs.CreateClubView.as_view(), name='create_club'),

    path('club/<str:club_url_name>/', views.ClubDashboardView.as_view(), name='club_dashboard'),
    path('club/<str:club_url_name>/members/', views.MembersListView.as_view(), name='member_list'),
    path('club/<str:club_url_name>/applicants/', views.ApplicantListView.as_view(), name='applicant_list'),
    path('club/<str:club_url_name>/edit/', views.EditClubView.as_view(), name='edit_club'),

    # '''Meeting URLs'''
    path('club/<str:club_url_name>/meetings/', views.MeetingListView.as_view(), name='meeting_list'),
    path('club/<str:club_url_name>/meetings/<int:meeting_id>/join', views.JoinMeetingView.as_view(),
         name='join_meeting'),
    path('club/<str:club_url_name>/meetings/<int:meeting_id>/leave', views.LeaveMeetingView.as_view(),
         name='leave_meeting'),
    path('club/<str:club_url_name>/meetings/<int:meeting_id>/', views.MeetingDetailsView.as_view(),
         name='meeting_details'),
    path('club/<str:club_url_name>/meetings/<int:meeting_id>/participants/', views.MeetingParticipantsView.as_view(),
         name='meeting_participants'),
    path('club/<str:club_url_name>/meetings/create/', views.CreateMeetingView.as_view(), name='create_meeting'),
    path('club/<str:club_url_name>/meetings/<int:meeting_id>/delete/', views.DeleteMeetingView.as_view(),
         name='delete_meeting'),

    # '''Library URLs'''
    path('library/', views.library_dashboard, name='library_dashboard'),
    path('library/books/', views.BookListView.as_view(), name='library_books'),  # searching and book table
    path('library/books/<int:book_id>/', views.BookDetailView.as_view(), name='book_view'),  # book view
    path('library/books/<int:book_id>/reviews/', views.BookReviewListView.as_view(), name='book_reviews'),

    # '''Review URLs'''
    path('library/books/<int:book_id>/create/', views.CreateReviewView.as_view(), name='create_review'),
    # create review for book represented by id
    path('library/books/<int:book_id>/edit/', views.EditReviewView.as_view(), name='edit_review'),
    # path('library/review/<int:book_id/delete') # delete review for book represented by id
    path('library/books/<int:book_id>/delete/', views.DeleteReviewView.as_view(), name='delete_review'),
    # delete review for book represented by id

    # '''BookList URLs'''
    path('user/<slug:username>/lists', views.BooklistListView.as_view(), name='booklists_list'),
    path('user/<slug:username>/lists/<int:booklist_id>', views.UserBookListView.as_view(), name='user_booklist'),
    path('user/<slug:username>/lists/create', views.CreateBookListView.as_view(), name='create_booklist'),
]
