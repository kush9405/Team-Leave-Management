from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, filters
from .models import Leave_Record
from .serializers import LeaveRecordSerializer

class LeaveRecordViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing leave records

    Provides CRUD operations:
    - GET /leaves/ - List all leave records
    - POST /leaves/ - Create a new leave record
    - GET /leaves/{id}/ - Retrieve a specific leave record
    - PUT /leaves/{id}/ - Update a leave record
    - PATCH /leaves/{id}/ - Partially update a leave record
    - DELETE /leaves/{id}/ - Delete a leave record

    Filtering available by:
    - Employee_Name
    - Leave_Type
    - Status
    - Start_Date
    - End_Date

    Search available by:
    - Employee_Name
    """
    queryset = Leave_Record.objects.all().order_by('-Start_Date')
    serializer_class = LeaveRecordSerializer

    # Permissions: Allow read-only for anyone, write for authenticated users
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    # Filtering and search
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    # Fields to filter on
    filterset_fields = {
        'Employee_Name': ['exact', 'contains', 'startswith','endswith','icontains'],
        'Leave_Type': ['exact'],
        'Status': ['exact'],
        'Start_Date': ['exact', 'gte', 'lte'],
        'End_Date': ['exact', 'gte', 'lte'],
    }

    # Fields to search on
    search_fields = ['Employee_Name', 'Leave_Type', 'Status']

    # Fields to order by
    ordering_fields = ['Start_Date', 'End_Date', 'Employee_Name']
    ordering = ['-Start_Date']  # Default ordering

    def perform_create(self, serializer):
        """
        Automatically assign leave record to logged-in user.
        Regular employees: Employee_Name set to their username
        Admin users: Can specify any Employee_Name
        """
        # If user is authenticated and is NOT admin
        if self.request.user.is_authenticated and not (self.request.user.is_staff or self.request.user.is_superuser):
            # Force Employee_Name to be the logged-in user's username
            serializer.save(Employee_Name=self.request.user.username)
        else:
            # Admin can specify any Employee_Name, or save as-is
            serializer.save()

    def get_queryset(self):
        """
        Return leaves based on user role:
        - Admin users → All leave records
        - Regular users → Only their own leave records
        """
        queryset = super().get_queryset()
        if not self.request.user.is_authenticated:

        # Check if user is authenticated
            # Anonymous users can  nothing
            return queryset.none()  # Return empty queryset

        # Check if user is admin (has is_staff or is_superuser flag)
        if  self.request.user.is_superuser:
            # Admin sees all records
            return queryset

        # Regular employee - only see their own leaves
        return queryset.filter(Employee_Name=self.request.user.username)

