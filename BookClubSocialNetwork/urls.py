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
from django.urls import path, include
from BookClub import views
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView
from django.contrib.auth import views as auth_views

from BookClub.models.recommendations import UserRecommendations

urlpatterns = [
    # '''Core URLs'''
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('favicon.ico'))),

    # '''Authentication URLs'''
    path('login/', views.LogInView.as_view(), name='login'),
    path('sign_up/', views.SignUpView.as_view(), name='sign_up'),
    path('log_out/', views.LogOutView.as_view(), name='log_out'),
    path('verification/', include('verify_email.urls')),

    path('reset_password/', auth_views.PasswordResetView.as_view(template_name='reset_password/reset_password.html', html_email_template_name='reset_password/password_reset_email.html'), name='reset_password'),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name='reset_password/reset_password_sent.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='reset_password/reset_password_form.html'), name='password_reset_confirm'),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='reset_password/reset_password_complete.html'), name='password_reset_complete'),


    # '''User URLs'''
    path('user/', views.UserDashboardView.as_view(), name='user_dashboard'),
    path('edit_profile/', views.EditProfileView.as_view(), name='edit_profile'),
    path('password_change/', views.ChangePasswordView.as_view(), name='password_change'),
    path('delete_account/', views.DeleteUserAccountView.as_view(), name='delete_user_account'),

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
    path('applications/', views.ApplicationListView.as_view(), name='applications'),
    path('create/', views.CreateClubView.as_view(), name='create_club'),
    path('club/<str:club_url_name>/recommendations', views.RecommendationBaseView.as_view(), name='club_recommendations'),

    path('club/<str:club_url_name>/', views.ClubDashboardView.as_view(), name='club_dashboard'),
    path('club/<str:club_url_name>/members/', views.MembersListView.as_view(), name='member_list'),
    path('club/<str:club_url_name>/edit/', views.EditClubView.as_view(), name='edit_club'),
    path('club/<str:club_url_name>/applicants/', views.ApplicantListView.as_view(), name='applicant_list'),
    path('club/<str:club_url_name>/edit/', views.EditClubView.as_view(), name='edit_club'),
    path('club/<str:club_url_name>/polls/create/', views.CreateClubPollView.as_view(), name='create_club_poll'),

    # '''Club Forum URLs'''
    path('club/<str:club_url_name>/forum/', views.ForumView.as_view(), name='club_forum'),
    path('club/<str:club_url_name>/forum/post/', views.CreatePostView.as_view(), name='create_forum_post'),
    path('club/<str:club_url_name>/forum/<int:post_id>/', views.ForumPostView.as_view(), name='forum_post'),
    path('club/<str:club_url_name>/forum/<int:post_id>/comment/',
         views.CreateCommentView.as_view(), name='create_forum_comment'),
    path('club/<str:club_url_name>/forum/<int:post_id>/comment/<int:comment_id>/delete/',
         views.DeleteForumCommentView.as_view(), name='delete_forum_comment'),
    path('club/<str:club_url_name>/forum/<int:post_id>/edit/',
         views.EditForumPostView.as_view(), name='edit_forum_post'),
    path('club/<str:club_url_name>/forum/<int:post_id>/delete/',
         views.DeleteForumPostView.as_view(), name='delete_forum_post'),

    # '''Meeting URLs'''
    path('club/<str:club_url_name>/meetings/<int:meeting_id>/edit/',views.EditMeetingView.as_view(), name='edit_meeting'),
    path('club/<str:club_url_name>/meetings/<int:meeting_id>/edit/remove_member/<int:member_id>', views.RemoveMeetingMember.as_view(), name='remove_meeting_member'),
    path('club/<str:club_url_name>/meetings/',views.MeetingListView.as_view(),name='meeting_list'),
    path('club/<str:club_url_name>/meetings/<int:meeting_id>/join/', views.JoinMeetingView.as_view(), name='join_meeting'),
    path('club/<str:club_url_name>/meetings/<int:meeting_id>/leave/', views.LeaveMeetingView.as_view(), name='leave_meeting'),
    path('club/<str:club_url_name>/meetings/<int:meeting_id>/', views.MeetingDetailsView.as_view(), name='meeting_details'),
    path('club/<str:club_url_name>/meetings/<int:meeting_id>/participants/', views.MeetingParticipantsView.as_view(), name='meeting_participants'),
    path('club/<str:club_url_name>/meetings/create/', views.CreateMeetingView.as_view(), name='create_meeting'),
    path('club/<str:club_url_name>/meetings/<int:meeting_id>/delete/', views.DeleteMeetingView.as_view(),
         name='delete_meeting'),
    


    # '''Library URLs'''
    path('library/', views.library_dashboard, name='library_dashboard'),
    path('library/books/', views.BookListView.as_view(), name='library_books'),  # searching and book table
    path('library/books/add_to_book_list/', views.AddToBookListView.as_view(), name='add_to_book_list'),
    path('library/books/<int:book_id>/', views.BookDetailView.as_view(), name='book_view'),  # book view
    path('library/books/<int:book_id>/reviews/', views.BookReviewListView.as_view(), name='book_reviews'),
    path('library/recommendations/', views.RecommendationBaseView.as_view(),
         name='user_recommendations'),

    # '''Review URLs'''
    path('library/books/<int:book_id>/create/', views.CreateReviewView.as_view(), name='create_review'),
    path('library/books/<int:book_id>/edit/', views.EditReviewView.as_view(), name='edit_review'),
    path('library/books/<int:book_id>/delete/', views.DeleteReviewView.as_view(), name='delete_review'),
    path('library/books/<int:book_id>/review/<int:review_id>/', views.ReviewDetailView.as_view(), name='book_review'),
    path('library/books/<int:book_id>/review/<int:review_id>/comment/', views.CreateCommentForReviewView.as_view(), name='comment_review'),
    path('library/books/<int:book_id>/review/<int:review_id>/comment/<int:comment_id>/delete/',
        views.DeleteCommentForReviewView.as_view(), name='delete_review_comment'),

    # '''Forum URLs'''
    path('forum/', views.ForumView.as_view(), name='global_forum'),
    path('forum/post/', views.CreatePostView.as_view(), name='create_forum_post'),
    path('forum/<int:post_id>/', views.ForumPostView.as_view(), name='forum_post'),
    path('forum/<int:post_id>/comment/', views.CreateCommentView.as_view(), name='create_forum_comment'),
    path('forum/<int:post_id>/edit/', views.EditForumPostView.as_view(), name='edit_forum_post'),
    path('forum/<int:post_id>/delete/', views.DeleteForumPostView.as_view(), name='delete_forum_post'),
    path('forum/<int:post_id>/comment/<int:comment_id>/delete/', views.DeleteForumCommentView.as_view(), name='delete_forum_comment'),
    path('forum/upvote/', views.CreateVoteView.as_view(), name='upvote'),
    path('forum/downvote/', views.CreateVoteView.as_view(), name='downvote'),

    # '''Book List URLs'''
    path('user/<str:username>/lists/',
         views.BooklistListView.as_view(), name='booklists_list'),
    path('user/<str:username>/lists/create/',
         views.CreateBookListView.as_view(), name='create_booklist'),
    path('user/<str:username>/list/<int:list_id>/delete/',
         views.DeleteBookListView.as_view(), name='delete_booklist'),
    path('user/<str:username>/lists/<int:booklist_id>/edit/',
         views.EditBookListView.as_view(), name='edit_booklist'),
    path('user/<str:username>/lists/<int:booklist_id>/',
         views.UserBookListView.as_view(), name='user_booklist'),
    path('user/<str:username>/lists/<int:booklist_id>/<int:book_id>/delete', views.RemoveFromBookListView.as_view(), name='remove_book'),
    

    # '''Agenda URLs'''
    path('agenda/', views.AgendaView.as_view(), name='agenda'),
    
    # '''Bookshelf URLs'''
    path('bookshelf/', views.BookShelfView.as_view(), name='bookshelf'),
    path('bookshelf/<int:book_id>/add/', views.AddToBookShelfView.as_view(), name='add_to_bookshelf'),
    path('bookshelf/<int:book_id>/update/', views.UpdateBookShelfView.as_view(), name='update_from_bookshelf'),
    path('bookshelf/<int:book_id>/remove/', views.RemoveFromBookShelfView.as_view(), name='remove_from_bookshelf'),
    
    # '''Asyn Views'''
    path('search_books/', views.BookSearchView.as_view(), name='async_book_search'),
    path('user_recommendations/', views.RecommendationUserListView.as_view(), name='async_user_recommendations'),
    path('club_recommendations/<str:club_url_name>/', views.RecommendationClubListView.as_view(), name='async_club_recommendations'),
]
