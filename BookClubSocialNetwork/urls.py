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

urlpatterns = [
    # '''Core URLs'''
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    
    # '''Authentication URLs'''
    path('login/', views.LogInView.as_view(), name='login'),
    path('sign_up/', views.SignUpView.as_view(), name='sign_up'),
    path('log_out/', views.LogOutView.as_view(), name='log_out'),
    
    # '''User URLs'''
    path('user_dashboard/', views.user_dashboard, name='user_dashboard'),
    
    # '''Club URLs'''
    path('club_dashboard/', views.club_dashboard, name='club_dashboard'),
    
    
]
