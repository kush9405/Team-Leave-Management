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
from django.http import JsonResponse

# Import HTMX views from the dedicated htmx_views module
from leaves.htmx_views.htmx import (
    render_leaves_table,
    render_leave_detail,
    render_my_leaves_table,
    render_edit_leave_form,
    update_leave,
    cancel_leave,
)

# Import authentication utilities
from authentication.utils import get_leave_stats


urlpatterns = [
    path('leaves/', include('leaves.urls')),  # API endpoints for leaves app
    path('api/', include('authentication.urls')),  # API endpoints for authentication
    path('dashboard/', TemplateView.as_view(template_name='dashboard.html'), name='dashboard'),
    path('register/', TemplateView.as_view(template_name='register.html'), name='register'),
    path('admin/', TemplateView.as_view(template_name='admin_dashboard.html'), name='admin_dashboard'),
    path('login/', TemplateView.as_view(template_name='login.html'), name='login'),
    path('admin-panel/', admin.site.urls),  # Django admin panel
    # HTMX endpoints for admin dashboard
    path('htmx/leaves/', render_leaves_table, name='htmx_leaves'),
    path('htmx/leaves/<int:id>/', render_leave_detail, name='htmx_leave_detail'),
    
    # HTMX endpoints for employee dashboard
    path('htmx/my-leaves/', render_my_leaves_table, name='htmx_my_leaves'),
    path('htmx/my-leaves/<int:id>/', render_leave_detail, name='htmx_my_leave_detail'),
    path('htmx/my-leaves/<int:leave_id>/edit/', render_edit_leave_form, name='htmx_edit_leave'),
    path('htmx/my-leaves/<int:leave_id>/update/', update_leave, name='htmx_update_leave'),
    path('htmx/my-leaves/<int:leave_id>/cancel/', cancel_leave, name='htmx_cancel_leave'),
    
    # Stats endpoint
    path('api/stats/', lambda request: JsonResponse(get_leave_stats(request)), name='api_stats'),
]
