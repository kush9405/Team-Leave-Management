from rest_framework import permissions
from .models import Role


class IsAdmin(permissions.BasePermission):
    """
    Allows access only to admin users.
    """
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            (request.user.role == Role.ADMIN or request.user.is_superuser)
        )


class IsManager(permissions.BasePermission):
    """
    Allows access to managers and admins.
    """
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            (request.user.role == Role.MANAGER or
             request.user.role == Role.ADMIN or
             request.user.is_superuser)
        )


class IsEmployee(permissions.BasePermission):
    """
    Allows access to employees, managers, and admins.
    """
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role in [Role.EMPLOYEE, Role.MANAGER, Role.ADMIN]
        )


class IsAdminOrManager(permissions.BasePermission):
    """
    Allows access to admins and managers for management operations.
    """
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role in [Role.ADMIN, Role.MANAGER]
        )
    
    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Allows access if user is owner or admin.
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser or request.user.role == Role.ADMIN:
            return True
        
        return obj.id == request.user.id


class IsVerified(permissions.BasePermission):
    """
    Allows access only to verified users.
    """
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_verified
        )


class IsAuthenticated(permissions.BasePermission):
    """
    Allows access to any authenticated user.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


class IsReadOnly(permissions.BasePermission):
    """
    Allows read-only access to any user (authenticated or not).
    """
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS

