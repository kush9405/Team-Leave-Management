from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


class Role(models.TextChoices):
    ADMIN = 'ADMIN', 'Admin'
    MANAGER = 'MANAGER', 'Manager'
    EMPLOYEE = 'EMPLOYEE', 'Employee'


class CustomUser(AbstractUser):
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    password = models.CharField(max_length=128)
    
    # Role-based fields
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.EMPLOYEE
    )
    is_verified = models.BooleanField(default=False)
    
    # Social auth fields
    social_id = models.CharField(max_length=100, blank=True, null=True)
    social_provider = models.CharField(max_length=20, blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"
    
    @property
    def is_admin(self):
        return self.role == Role.ADMIN or self.is_superuser
    
    @property
    def is_manager(self):
        return self.role == Role.MANAGER or self.is_admin
    
    @property
    def is_employee(self):
        return self.role == Role.EMPLOYEE
