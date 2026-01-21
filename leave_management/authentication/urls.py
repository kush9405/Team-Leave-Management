from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    LoginView, RegisterView, LogoutView, UserMeView,
    GoogleOAuthView, GitHubOAuthView,
    GoogleAuthURLView, GitHubAuthURLView,
    GoogleOAuthCallbackView
)

urlpatterns = [
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/me/', UserMeView.as_view(), name='me'),
    path('auth/google/', GoogleOAuthView.as_view(), name='google_oauth'),
    path('auth/github/', GitHubOAuthView.as_view(), name='github_oauth'),
    path('auth/google_auth_url/', GoogleAuthURLView.as_view(), name='google_auth_url'),
    path('auth/github_auth_url/', GitHubAuthURLView.as_view(), name='github_auth_url'),
    path('auth/google/callback/', GoogleOAuthCallbackView.as_view(), name='google_callback'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

