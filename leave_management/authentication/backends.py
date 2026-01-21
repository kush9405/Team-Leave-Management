from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

CustomUser = get_user_model()


class CustomUserAuthBackend(ModelBackend):
    """
    Custom authentication backend that authenticates using email or username
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate user with email or username and password
        """
        if username is None:
            username = kwargs.get(CustomUser.USERNAME_FIELD)
        
        if username is None or password is None:
            return None
        
        try:
            # Try to find user by email or username
            user = CustomUser.objects.get(
                Q(email__iexact=username) | 
                Q(username__iexact=username)
            )
        except CustomUser.DoesNotExist:
            return None
        
        # Check password
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        
        return None
    
    def user_can_authenticate(self, user):
        """
        Reject users with is_active=False
        """
        return getattr(user, 'is_active', True)

    def get_user(self, user_id):
        """
        Retrieve user by ID
        """
        try:
            return CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return None

