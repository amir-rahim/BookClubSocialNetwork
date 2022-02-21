from django.contrib import admin
from django.urls import path
from BookClub import views
from BookClub.tests.helpers_tests.test_rank_required_mixin import TestView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('login/', views.LogInView.as_view(), name='login'),
    path('sign_up/', views.SignUpView.as_view(), name='sign_up'),
    path('log_out/', views.LogOutView.as_view(), name='log_out'),
    path('test_rank_required/', TestView.as_view(), name = 'test_rank_required'),
]