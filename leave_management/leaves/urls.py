from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LeaveRecordViewSet  # Import from the main views.py file

# Create a router and register the ViewSet
router = DefaultRouter()
router.register(r'leaves', LeaveRecordViewSet, basename='leave')

urlpatterns = [
    path('', include(router.urls)),
]

