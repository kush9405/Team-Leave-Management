#!/usr/bin/env python
import os
import sys

sys.path.insert(0, '/home/ext_kushagra.agarwal/Team-Leave-Management')
sys.path.insert(0, '/home/ext_kushagra.agarwal/Team-Leave-Management/leave_management')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'leave_management.settings')

import django
django.setup()

from authentication.models import CustomUser, Role

# Create or update admin user
admin_email = 'admin@example.com'
admin_username = 'admin'
admin_password = 'admin123'

user, created = CustomUser.objects.get_or_create(
    email=admin_email,
    defaults={
        'username': admin_username,
        'role': Role.ADMIN,
        'is_staff': True,
        'is_superuser': True,
        'is_verified': True,
    }
)

user.set_password(admin_password)
user.role = Role.ADMIN
user.is_staff = True
user.is_superuser = True
user.is_verified = True
user.save()

if created:
    print(f'✓ Admin user created successfully!')
else:
    print(f'✓ Admin user updated successfully!')

print(f'')
print(f'Credentials:')
print(f'  Email: {admin_email}')
print(f'  Username: {admin_username}')
print(f'  Password: {admin_password}')
print(f'  Role: {user.role}')
print(f'  Is Staff: {user.is_staff}')
print(f'  Is Superuser: {user.is_superuser}')
print(f'')
print(f'API Endpoints:')
print(f'  POST /api/auth/login/ - Login with email/password')
print(f'  POST /api/auth/register/ - Register new user')
print(f'  POST /api/auth/google/ - Google OAuth login')
print(f'  POST /api/auth/github/ - GitHub OAuth login')
print(f'  GET /api/auth/me/ - Get current user')
print(f'  POST /api/auth/logout/ - Logout')
print(f'  POST /api/auth/token/refresh/ - Refresh token')

