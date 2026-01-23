from django.contrib import admin
from .models import Leave_Record


@admin.register(Leave_Record)
class LeaveRecordAdmin(admin.ModelAdmin):
    """Admin configuration for Leave_Record model"""
    list_display = ['id', 'Employee_Name', 'Leave_Type', 'Status', 'Start_Date', 'End_Date', 'Applied_On']
    list_filter = ['Status', 'Leave_Type']
    search_fields = ['Employee_Name', 'Reason']
    ordering = ['-Applied_On']
    readonly_fields = ['Applied_On']

    # Organize fields in fieldsets
    fieldsets = (
        ('Employee Information', {
            'fields': ('Employee_Name',)
        }),
        ('Leave Details', {
            'fields': ('Leave_Type', 'Start_Date', 'End_Date', 'No_of_Days', 'Reason')
        }),
        ('Status', {
            'fields': ('Status', 'Applied_On')
        }),
        ('Manager Response', {
            'fields': ('Manager_Response', 'Manager_Name', 'Responded_On', 'cancelled_by', 'cancelled_on'),
            'classes': ('collapse',)  # Collapsible section
        }),
    )
