#!/usr/bin/env python
import os
import sys

sys.path.insert(0, '/home/ext_kushagra.agarwal/Team-Leave-Management')
sys.path.insert(0, '/home/ext_kushagra.agarwal/Team-Leave-Management/leave_management')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'leave_management.settings')

import django
django.setup()

from authentication.models import CustomUser

# Create superuser
CustomUser.objects.create_superuser(
    username='admin',
    email='admin@example.com',
    password='admin123'
)

print('Superuser created successfully!')
print('Username: admin')
print('Password: admin123')


