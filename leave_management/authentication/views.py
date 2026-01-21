import json
import requests
from django.conf import settings
from rest_framework import status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from django.db import models

from .models import CustomUser, Role
from .serializers import (
    UserSerializer, LoginSerializer, RegisterSerializer,
    GoogleOAuthSerializer, GitHubOAuthSerializer
)


class LoginView(APIView):
    """
    POST /api/auth/login/
    Login with email and password
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        
        response_data = {
            'message': 'Login successful',
            'user': UserSerializer(user).data,
            'tokens': {
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
                'token_type': 'Bearer',
            }
        }
        
        response = Response(response_data, status=status.HTTP_200_OK)
        response.setdefault('Access-Control-Allow-Origin', '*')
        return response


class RegisterView(APIView):
    """
    POST /api/auth/register/
    Register a new user
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        
        response_data = {
            'message': 'Registration successful',
            'user': UserSerializer(user).data,
            'tokens': {
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
                'token_type': 'Bearer',
            }
        }
        
        return Response(response_data, status=status.HTTP_201_CREATED)


class LogoutView(APIView):
    """
    POST /api/auth/logout/
    Logout user (blacklist refresh token)
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            return Response({
                'message': 'Logout successful'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'message': 'Logout processed'
            }, status=status.HTTP_200_OK)


class UserMeView(APIView):
    """
    GET /api/auth/me/
    Get current user info
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        # For JWT authentication, request.user might be a lazy user object
        # Check if user has an id attribute (which indicates a valid user)
        if not hasattr(request.user, 'id') or request.user.id is None:
            return Response({
                'error': 'Authentication required'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        return Response({
            'user': UserSerializer(request.user).data
        })


class GoogleOAuthView(APIView):
    """
    POST /api/auth/google/
    Login/Register with Google OAuth
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = GoogleOAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        id_token_string = serializer.validated_data['id_token']
        
        try:
            # Verify the Google ID token
            idinfo = id_token.verify_oauth2_token(
                id_token_string,
                google_requests.Request(),
                settings.GOOGLE_OAUTH_CLIENT_ID
            )
            
            google_id = idinfo['sub']
            email = idinfo.get('email')
            username = idinfo.get('name', email.split('@')[0])
            
            # Check if user exists
            user = CustomUser.objects.filter(
                models.Q(social_id=google_id) |
                models.Q(email=email)
            ).first()
            
            if user:
                # Update social info if needed
                if user.social_id != google_id:
                    user.social_id = google_id
                    user.social_provider = 'google'
                    user.save()
            else:
                # Create new user
                user = CustomUser.objects.create(
                    username=username[:50] if len(username) > 50 else username,
                    email=email,
                    social_id=google_id,
                    social_provider='google',
                    is_verified=True,
                    role=Role.EMPLOYEE
                )
            
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'message': 'Google login successful',
                'user': UserSerializer(user).data,
                'tokens': {
                    'access_token': str(refresh.access_token),
                    'refresh_token': str(refresh),
                    'token_type': 'Bearer',
                }
            })
            
        except ValueError:
            return Response({
                'error': 'Invalid Google ID token'
            }, status=status.HTTP_400_BAD_REQUEST)


class GitHubOAuthView(APIView):
    """
    POST /api/auth/github/
    Login/Register with GitHub OAuth
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = GitHubOAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        code = serializer.validated_data['code']
        
        # Exchange code for access token
        token_url = 'https://github.com/login/oauth/access_token'
        token_data = {
            'client_id': settings.GITHUB_OAUTH_CLIENT_ID,
            'client_secret': settings.GITHUB_OAUTH_CLIENT_SECRET,
            'code': code
        }
        token_headers = {'Accept': 'application/json'}
        
        token_response = requests.post(
            token_url, data=token_data, headers=token_headers
        )
        token_json = token_response.json()
        
        access_token = token_json.get('access_token')
        
        if not access_token:
            return Response({
                'error': 'Failed to get access token from GitHub'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get user info from GitHub
        user_url = 'https://api.github.com/user'
        user_headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json'
        }
        
        user_response = requests.get(user_url, headers=user_headers)
        user_data = user_response.json()
        
        github_id = str(user_data.get('id'))
        email = user_data.get('email')
        username = user_data.get('login')
        
        if not email:
            # Get user email if not public
            emails_response = requests.get(
                'https://api.github.com/user/emails',
                headers=user_headers
            )
            emails = emails_response.json()
            primary_email = next(
                (e for e in emails if e.get('primary')), 
                emails[0] if emails else None
            )
            email = primary_email.get('email') if primary_email else f'{username}@github.local'
        
        # Check if user exists
        user = CustomUser.objects.filter(
            models.Q(social_id=github_id) |
            models.Q(email=email)
        ).first()
        
        if user:
            if user.social_id != github_id:
                user.social_id = github_id
                user.social_provider = 'github'
                user.save()
        else:
            user = CustomUser.objects.create(
                username=username,
                email=email,
                social_id=github_id,
                social_provider='github',
                is_verified=True,
                role=Role.EMPLOYEE
            )
        
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'GitHub login successful',
            'user': UserSerializer(user).data,
            'tokens': {
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
                'token_type': 'Bearer',
            }
        })


class GoogleAuthURLView(APIView):
    """
    GET /api/auth/google_auth_url/
    Get Google OAuth URL for redirect
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        from django.urls import reverse
        
        redirect_uri = request.build_absolute_uri('/api/auth/google/callback/')
        
        google_auth_url = (
            f"https://accounts.google.com/o/oauth2/v2/auth?"
            f"client_id={settings.GOOGLE_OAUTH_CLIENT_ID}"
            f"&redirect_uri={redirect_uri}"
            f"&response_type=code"
            f"&scope=openid email profile"
            f"&access_type=offline"
        )
        
        return Response({
            'auth_url': google_auth_url
        })


class GoogleOAuthCallbackView(APIView):
    """
    GET /api/auth/google/callback/
    Handle Google OAuth callback - redirect to frontend with tokens
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        import requests
        
        code = request.GET.get('code')
        error = request.GET.get('error')
        
        if error:
            return Response({
                'error': f'Google OAuth error: {error}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not code:
            return Response({
                'error': 'No authorization code received'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Exchange code for access token
            token_url = 'https://oauth2.googleapis.com/token'
            token_data = {
                'code': code,
                'client_id': settings.GOOGLE_OAUTH_CLIENT_ID,
                'client_secret': settings.GOOGLE_OAUTH_CLIENT_SECRET,
                'redirect_uri': request.build_absolute_uri('/api/auth/google/callback/'),
                'grant_type': 'authorization_code'
            }
            
            token_response = requests.post(token_url, data=token_data)
            token_json = token_response.json()
            
            if 'access_token' not in token_json:
                return Response({
                    'error': 'Failed to exchange code for token',
                    'details': token_json
                }, status=status.HTTP_400_BAD_REQUEST)
            
            access_token = token_json['access_token']
            
            # Get user info from Google
            user_info_url = 'https://www.googleapis.com/oauth2/v2/userinfo'
            user_headers = {'Authorization': f'Bearer {access_token}'}
            user_response = requests.get(user_info_url, headers=user_headers)
            user_data = user_response.json()
            
            google_id = user_data.get('id')
            email = user_data.get('email')
            username = user_data.get('name', email.split('@')[0])
            
            # Check if user exists
            user = CustomUser.objects.filter(
                models.Q(social_id=google_id) |
                models.Q(email=email)
            ).first()
            
            if user:
                # Update social info if needed
                if user.social_id != google_id:
                    user.social_id = google_id
                    user.social_provider = 'google'
                    user.save()
            else:
                # Create new user
                user = CustomUser.objects.create(
                    username=username[:50] if len(username) > 50 else username,
                    email=email,
                    social_id=google_id,
                    social_provider='google',
                    is_verified=True,
                    role=Role.EMPLOYEE
                )
            
            refresh = RefreshToken.for_user(user)
            
            # Redirect to auth callback page with tokens
            # Note: For production, consider using HTTP-only cookies instead of URL params
            from django.urls import reverse
            callback_url = request.build_absolute_uri(reverse('auth_callback'))
            redirect_url = (
                f"{callback_url}"
                f"?access_token={str(refresh.access_token)}"
                f"&refresh_token={str(refresh)}"
                f"&token_type=Bearer"
            )
            
            from django.shortcuts import redirect
            return redirect(redirect_url)
            
        except Exception as e:
            return Response({
                'error': f'OAuth callback error: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GitHubAuthURLView(APIView):
    """
    GET /api/auth/github_auth_url/
    Get GitHub OAuth URL for redirect
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        redirect_uri = request.build_absolute_uri('/api/auth/github/callback/')
        
        github_auth_url = (
            f"https://github.com/login/oauth/authorize?"
            f"client_id={settings.GITHUB_OAUTH_CLIENT_ID}"
            f"&redirect_uri={redirect_uri}"
            f"&scope=read:user user:email"
        )
        
        return Response({
            'auth_url': github_auth_url
        })


class TokenRefreshView(APIView):
    """
    POST /api/auth/token/refresh/
    Refresh access token
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        refresh_token = request.data.get('refresh_token')
        
        if not refresh_token:
            return Response({
                'error': 'Refresh token required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)
            
            return Response({
                'access_token': access_token,
                'token_type': 'Bearer',
            })
        except Exception as e:
            return Response({
                'error': 'Invalid refresh token'
            }, status=status.HTTP_401_UNAUTHORIZED)

