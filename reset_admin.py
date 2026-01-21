#!/usr/bin/env python
import os
import sys

sys.path.insert(0, '/home/ext_kushagra.agarwal/Team-Leave-Management')
sys.path.insert(0, '/home/ext_kushagra.agarwal/Team-Leave-Management/leave_management')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'leave_management.settings')

import django
django.setup()

from authentication.models import CustomUser

try:
    user = CustomUser.objects.get(username='admin')
    user.set_password('admin123')
    user.save()
    print('Password reset successfully!')
    print(f'Username: admin')
    print(f'Password: admin123')
    print(f'Is staff: {user.is_staff}')
    print(f'Is superuser: {user.is_superuser}')
except CustomUser.DoesNotExist:
    print('User admin does not exist')

