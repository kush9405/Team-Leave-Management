import json
import requests
from django.conf import settings
from rest_framework import status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import models

from .models import CustomUser, Role
from .serializers import (
    UserSerializer, LoginSerializer, RegisterSerializer
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


class PromoteUserView(APIView):
    """
    POST /api/auth/promote/
    Promote a user to admin (admin only)
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # Check if current user is admin
        if not hasattr(request.user, 'role') or request.user.role not in ['ADMIN', 'MANAGER']:
            return Response({
                'error': 'Only admins can promote users'
            }, status=status.HTTP_403_FORBIDDEN)
        
        user_id = request.data.get('user_id')
        new_role = request.data.get('role')
        
        if not user_id:
            return Response({
                'error': 'user_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if new_role not in [role[0] for role in Role.choices]:
            return Response({
                'error': f'Invalid role. Must be one of: {[r[0] for r in Role.choices]}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = CustomUser.objects.get(id=user_id)
            old_role = user.role
            user.role = new_role
            user.save()
            
            return Response({
                'message': f'User {user.username} promoted from {old_role} to {new_role}',
                'user': UserSerializer(user).data
            })
        except CustomUser.DoesNotExist:
            return Response({
                'error': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)


class UsersListView(APIView):
    """
    GET /api/users/
    Get all users (admin only)
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Check if current user is admin
        if not hasattr(request.user, 'role') or request.user.role not in ['ADMIN', 'MANAGER']:
            return Response({
                'error': 'Only admins can view all users'
            }, status=status.HTTP_403_FORBIDDEN)
        
        users = CustomUser.objects.all().order_by('-created_at')
        return Response({
            'users': UserSerializer(users, many=True).data
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

