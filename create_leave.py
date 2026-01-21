#!/usr/bin/env python
import os
import sys

sys.path.insert(0, '/home/ext_kushagra.agarwal/Team-Leave-Management')
sys.path.insert(0, '/home/ext_kushagra.agarwal/Team-Leave-Management/leave_management')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'leave_management.settings')

import django
django.setup()

from datetime import date
from leaves.models import Leave_Record

# Create leave record
leave = Leave_Record.objects.create(
    Employee_Name='Akshay',
    Leave_Type='SICK',
    Start_Date=date(2024, 1, 15),
    End_Date=date(2024, 1, 16),
    Status='PENDING'
)

print('Leave record created!')
print('ID:', leave.id)
print('Employee:', leave.Employee_Name)
print('Type:', leave.Leave_Type)
print('Dates:', leave.Start_Date, 'to', leave.End_Date)
print('Status:', leave.Status)

