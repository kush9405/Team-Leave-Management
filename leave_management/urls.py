"""
URL configuration for leave_management project.
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Authentication API
    path('api/', include('authentication.urls')),
    
    # Leaves API
    path('', include('leaves.urls')),
    
    # Template views
    path('login/', TemplateView.as_view(template_name='login.html'), name='login'),
    path('dashboard/', TemplateView.as_view(template_name='dashboard.html'), name='dashboard'),
    path('admin/', TemplateView.as_view(template_name='admin_dashboard.html'), name='admin_dashboard'),
    path('auth/callback/', TemplateView.as_view(template_name='auth_callback.html'), name='auth_callback'),
    
    # HTMX endpoints
    path('htmx/leaves/', include('leaves.urls')),
]

