"""
URL configuration for leave_management project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.template.loader import render_to_string
from django.http import JsonResponse, HttpResponse
from leaves.models import Leave_Record


urlpatterns = [
    path('leaves/', include('leaves.urls')),  # API endpoints for leaves app
    path('api/', include('authentication.urls')),  # API endpoints for authentication
    # path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('auth/callback/', TemplateView.as_view(template_name='auth_callback.html'), name='auth_callback'),
    path('dashboard/', TemplateView.as_view(template_name='dashboard.html'), name='dashboard'),
    path('admin/', TemplateView.as_view(template_name='admin_dashboard.html'), name='admin_dashboard'),
    path('login/', TemplateView.as_view(template_name='login.html'), name='login'),
    
    # HTMX endpoints for admin dashboard
    path('htmx/leaves/', lambda request: render_leaves_table(request), name='htmx_leaves'),
    path('htmx/leaves/<int:id>/', lambda request, id: render_leave_detail(request, id), name='htmx_leave_detail'),
    
    # HTMX endpoints for employee dashboard
    path('htmx/my-leaves/', lambda request: render_my_leaves_table(request), name='htmx_my_leaves'),
    
    # Stats endpoint
    path('api/stats/', lambda request: JsonResponse(get_leave_stats(request)), name='api_stats'),
]


def get_leave_stats(request):
    """Get leave statistics"""
    if not request.user.is_authenticated:
        return {'total': 0, 'pending': 0, 'approved': 0, 'rejected': 0}
    
    if request.user.is_superuser or getattr(request.user, 'role', None) in ['ADMIN', 'MANAGER']:
        queryset = Leave_Record.objects.all()
    else:
        queryset = Leave_Record.objects.filter(Employee_Name=request.user.username)
    
    return {
        'total': queryset.count(),
        'pending': queryset.filter(Status='PENDING').count(),
        'approved': queryset.filter(Status='APPROVED').count(),
        'rejected': queryset.filter(Status='REJECTED').count(),
    }


def render_leaves_table(request):
    """Render HTMX fragment for leaves table"""
    # Build query params for filters
    query_params = request.GET.copy()
    
    # Remove HTMX headers
    query_params.pop('ordering', None)
    
    # Get ordering
    ordering = request.GET.get('ordering', '-Start_Date')
    
    # Check if user is admin
    is_admin = request.user.is_authenticated and (request.user.is_superuser or getattr(request.user, 'role', None) in ['ADMIN', 'MANAGER'])
    
    # Base queryset - admins see all, employees see only theirs
    if is_admin:
        queryset = Leave_Record.objects.all()
    elif request.user.is_authenticated:
        queryset = Leave_Record.objects.filter(Employee_Name=request.user.username)
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


def render_my_leaves_table(request):
    """Render HTMX fragment for employee's own leaves table - shows all leaves (no pending filter)"""
    
    # Get ordering
    ordering = request.GET.get('ordering', '-Start_Date')
    
    # Base queryset - employees see only their own leaves
    if request.user.is_authenticated:
        queryset = Leave_Record.objects.filter(Employee_Name=request.user.username)
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


def render_leave_detail(request, id):
    """Render HTMX fragment for leave detail"""
    try:
        leave = Leave_Record.objects.get(id=id)
    except Leave_Record.DoesNotExist:
        return HttpResponse('<p class="text-red-500">Leave request not found</p>')
    
    html = render_to_string('partials/leave_detail.html', {'leave': leave})
    return HttpResponse(html)
