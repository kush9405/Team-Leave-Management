"""
HTMX Views for Leave Management

This module contains view functions for HTMX partial rendering.
These views return HTML fragments for dynamic updates without full page reloads.
"""

from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone

from leaves.models import Leave_Record
from authentication.utils import get_user_from_request


def render_leaves_table(request):
    """
    Render HTMX fragment for leaves table (admin view).
    
    Supports filtering by:
    - Employee_Name: Filter by employee name (case-insensitive contains)
    - Leave_Type: Filter by leave type
    - Status: Filter by leave status (PENDING, APPROVED, REJECTED)
    - Start_Date__gte: Start date greater than or equal
    - End_Date__lte: End date less than or equal
    - search: General search on employee name
    - ordering: Sort field (default: -Start_Date)
    
    Returns:
        HttpResponse: HTML fragment for the leaves table
    """
    # Build query params for filters
    query_params = request.GET.copy()
    
    # Remove HTMX headers
    query_params.pop('ordering', None)
    
    # Get ordering
    ordering = request.GET.get('ordering', '-Start_Date')
    
    # Get authenticated user (supports JWT and session)
    user = get_user_from_request(request)
    
    # Check if user is admin
    is_admin = user and (user.is_superuser or getattr(user, 'role', None) in ['ADMIN', 'MANAGER'])
    
    # Base queryset - admins see all, employees see only theirs
    if is_admin:
        queryset = Leave_Record.objects.all()
    elif user:
        queryset = Leave_Record.objects.filter(Employee_Name=user.username)
    else:
        queryset = Leave_Record.objects.none()
    
    # Apply filters
    employee_name = request.GET.get('Employee_Name__icontains')
    if employee_name:
        queryset = queryset.filter(Employee_Name__icontains=employee_name)
    
    leave_type = request.GET.get('Leave_Type')
    if leave_type:
        queryset = queryset.filter(Leave_Type=leave_type)
    
    status = request.GET.get('Status')
    if status:
        queryset = queryset.filter(Status=status)
    # Note: No default status filter - show all leaves for both admin and employee
    
    start_date_gte = request.GET.get('Start_Date__gte')
    if start_date_gte:
        queryset = queryset.filter(Start_Date__gte=start_date_gte)
    
    end_date_lte = request.GET.get('End_Date__lte')
    if end_date_lte:
        queryset = queryset.filter(End_Date__lte=end_date_lte)
    
    # Search
    search = request.GET.get('search')
    if search:
        queryset = queryset.filter(Employee_Name__icontains=search)
    
    # Apply ordering
    queryset = queryset.order_by(ordering)
    
    # Get search for results count
    search_param = request.GET.get('search', '')
    status_param = request.GET.get('Status', '')
    
    html = render_to_string('partials/leaves_table.html', {
        'leaves': queryset,
        'search': search_param,
        'status_filter': status_param,
    })
    
    return HttpResponse(html)


def render_leave_detail(request, id):
    """
    Render HTMX fragment for leave detail.
    
    Args:
        request: HTTP request
        id: Leave record ID
    
    Returns:
        HttpResponse: HTML fragment for the leave detail or error message
    """
    user = get_user_from_request(request)
    
    try:
        leave = Leave_Record.objects.get(id=id)
    except Leave_Record.DoesNotExist:
        return HttpResponse('<p class="text-red-500">Leave request not found</p>')
    
    # Check if current user can edit this leave
    can_edit = user and leave.Employee_Name == user.username
    
    # Check if user is admin
    is_admin = user and (user.is_superuser or getattr(user, 'role', None) in ['ADMIN', 'MANAGER'])
    
    html = render_to_string('partials/leave_detail.html', {
        'leave': leave,
        'can_edit': can_edit,
        'is_admin': is_admin,
    })
    return HttpResponse(html)


def render_my_leaves_table(request):
    """
    Render HTMX fragment for employee's own leaves table.
    
    Shows all leaves for the authenticated employee (no default pending filter).
    Supports filtering by Leave_Type and Status.
    
    Args:
        request: HTTP request
    
    Returns:
        HttpResponse: HTML fragment for the employee's leaves table
    """
    # Get ordering
    ordering = request.GET.get('ordering', '-Start_Date')
    
    # Get authenticated user (supports JWT and session)
    user = get_user_from_request(request)
    
    # Base queryset - employees see only their own leaves
    if user:
        queryset = Leave_Record.objects.filter(Employee_Name=user.username)
    else:
        queryset = Leave_Record.objects.none()
    
    # Apply filters
    leave_type = request.GET.get('Leave_Type')
    if leave_type:
        queryset = queryset.filter(Leave_Type=leave_type)
    
    status = request.GET.get('Status')
    if status:
        queryset = queryset.filter(Status=status)
    # Note: No default status filter - show all leaves for employee
    
    # Apply ordering
    queryset = queryset.order_by(ordering)
    
    html = render_to_string('partials/employee_leaves_table.html', {
        'leaves': queryset,
    })
    
    return HttpResponse(html)


def render_edit_leave_form(request, leave_id):
    """
    Render HTMX fragment for edit leave form.
    
    Args:
        request: HTTP request
        leave_id: Leave record ID
    
    Returns:
        HttpResponse: HTML form for editing leave or error message
    """
    user = get_user_from_request(request)
    
    if not user:
        return HttpResponse('<p class="text-red-500">Please log in to edit leave</p>')
    
    try:
        leave = Leave_Record.objects.get(id=leave_id)
    except Leave_Record.DoesNotExist:
        return HttpResponse('<p class="text-red-500">Leave request not found</p>')
    
    # Check ownership and status
    if leave.Employee_Name != user.username:
        return HttpResponse('<p class="text-red-500">You can only edit your own leave requests</p>')
    
    if leave.Status != 'PENDING':
        return HttpResponse('<p class="text-red-500">Only PENDING leaves can be edited</p>')
    
    html = render_to_string('partials/edit_leave_form.html', {
        'leave': leave,
        'leave_types': Leave_Record.LEAVE_TYPES,
    })
    
    return HttpResponse(html)


def update_leave(request, leave_id):
    """
    Handle leave update via HTMX (PATCH request).
    
    Args:
        request: HTTP request
        leave_id: Leave record ID
    
    Returns:
        HttpResponse: Updated leave detail or error message
    """
    import json
    from django.http import QueryDict
    
    user = get_user_from_request(request)
    
    if not user:
        return HttpResponse('<p class="text-red-500">Please log in to update leave</p>')
    
    try:
        leave = Leave_Record.objects.get(id=leave_id)
    except Leave_Record.DoesNotExist:
        return HttpResponse('<p class="text-red-500">Leave request not found</p>')
    
    # Check ownership and status
    if leave.Employee_Name != user.username:
        return HttpResponse('<p class="text-red-500">You can only update your own leave requests</p>')
    
    if leave.Status != 'PENDING':
        return HttpResponse('<p class="text-red-500">Only PENDING leaves can be updated</p>')
    
    # Get form data - handle both form data and JSON
    content_type = request.content_type or ''
    
    if 'application/json' in content_type:
        # Parse JSON data
        try:
            data = json.loads(request.body)
            leave_type = data.get('Leave_Type')
            start_date = data.get('Start_Date')
            end_date = data.get('End_Date')
        except json.JSONDecodeError:
            return HttpResponse('<p class="text-red-500">Invalid JSON data</p>')
    else:
        # Parse form data
        leave_type = request.POST.get('Leave_Type')
        start_date = request.POST.get('Start_Date')
        end_date = request.POST.get('End_Date')

    if not leave_type or not start_date or not end_date:
        print(f"Error updating leave {leave.id}: leave_type={leave_type}, start_date={start_date}, end_date={end_date}")
        return HttpResponse('<p class="text-red-500">All fields are required</p>')
    
    # Update the leave
    leave.Leave_Type = leave_type
    leave.Start_Date = start_date
    leave.End_Date = end_date
    leave.save()
    
    # Return updated detail with context
    can_edit = True  # User just edited, so they can still edit
    is_admin = user and (user.is_superuser or getattr(user, 'role', None) in ['ADMIN', 'MANAGER'])
    
    html = render_to_string('partials/leave_detail.html', {
        'leave': leave,
        'can_edit': can_edit,
        'is_admin': is_admin,
    })
    return HttpResponse(html)


def cancel_leave(request, leave_id):
    """
    Handle leave cancellation via HTMX (PATCH request).
    
    Args:
        request: HTTP request
        leave_id: Leave record ID
    
    Returns:
        HttpResponse: Updated leave detail or error message
    """
    user = get_user_from_request(request)
    
    if not user:
        return HttpResponse('<p class="text-red-500">Please log in to cancel leave</p>')
    
    try:
        leave = Leave_Record.objects.get(id=leave_id)
    except Leave_Record.DoesNotExist:
        return HttpResponse('<p class="text-red-500">Leave request not found</p>')
    
    # Check ownership
    if leave.Employee_Name != user.username:
        return HttpResponse('<p class="text-red-500">You can only cancel your own leave requests</p>')
    
    # Check if cancellable
    if leave.Status not in ['PENDING', 'APPROVED']:
        return HttpResponse(f'<p class="text-red-500">Cannot cancel leave with status: {leave.Status}</p>')
    
    # Cancel the leave
    leave.Status = 'CANCELLED'
    leave.Cancelled_By = user.username
    leave.Cancelled_On = timezone.now()
    leave.save()
    
    # Return updated detail with context
    can_edit = False  # Cancelled leaves can't be edited
    is_admin = user and (user.is_superuser or getattr(user, 'role', None) in ['ADMIN', 'MANAGER'])
    
    html = render_to_string('partials/leave_detail.html', {
        'leave': leave,
        'can_edit': can_edit,
        'is_admin': is_admin,
    })
    return HttpResponse(html)

