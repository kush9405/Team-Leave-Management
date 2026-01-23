"""
Authentication utilities for Leave Management.

This module provides shared authentication functions used across
the application, including JWT token handling and user authentication.
"""

from django.contrib.auth.models import AnonymousUser

from authentication.models import CustomUser
from leaves.models import Leave_Record


def get_jwt_user(request):
    """
    Authenticate user from JWT token in Authorization header.
    Returns the user if authenticated, None otherwise.
    """
    from django.conf import settings
    import jwt
    
    auth_header = request.headers.get('Authorization', '')
    
    if not auth_header.startswith('Bearer '):
        return None
    
    token = auth_header[7:]  # Remove 'Bearer ' prefix
    
    try:
        # Decode the JWT token
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=['HS256'],
            options={'verify_exp': True}
        )
        
        # Get user ID from token payload
        user_id = payload.get('user_id')
        if user_id:
            user = CustomUser.objects.filter(id=user_id).first()
            return user
            
    except jwt.ExpiredSignatureError:
        print("JWT token has expired")
        return None
    except jwt.InvalidTokenError as e:
        print(f"JWT token error: {e}")
        return None
    except Exception as e:
        print(f"JWT Authentication error: {e}")
        return None
    
    return None


def get_user_from_request(request):
    """
    Get authenticated user - supports both session and JWT authentication.
    
    Args:
        request: HTTP request object
        
    Returns:
        CustomUser if authenticated, None otherwise
    """
    # First try JWT authentication (for API/HTMX requests)
    jwt_user = get_jwt_user(request)
    if jwt_user and not isinstance(jwt_user, AnonymousUser):
        return jwt_user
    
    # Fall back to session authentication
    if request.user and not isinstance(request.user, AnonymousUser):
        return request.user
    
    return None


def get_leave_stats(request):
    """
    Get leave statistics for the authenticated user.
    
    Args:
        request: HTTP request object
        
    Returns:
        dict: Leave statistics with total, pending, approved, rejected counts
    """
    user = get_user_from_request(request)
    
    if not user:
        return {'total': 0, 'pending': 0, 'approved': 0, 'rejected': 0}
    
    if user.is_superuser or getattr(user, 'role', None) in ['ADMIN', 'MANAGER']:
        queryset = Leave_Record.objects.all()
    else:
        queryset = Leave_Record.objects.filter(Employee_Name=user.username)
    
    return {
        'total': queryset.count(),
        'pending': queryset.filter(Status='PENDING').count(),
        'approved': queryset.filter(Status='APPROVED').count(),
        'rejected': queryset.filter(Status='REJECTED').count(),
    }

