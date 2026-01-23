from django.db import models

# Create your models here.
class Leave_Record(models.Model):
    LEAVE_TYPES = (
        ('SICK', 'Sick Leave'),
        ('CASUAL', 'Casual Leave'),
        ('EARNED', 'Earned Leave'),
    )
    STATUS_TYPES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('CANCELLED', 'Cancelled'),
    )

    Employee_Name = models.CharField(max_length=50, null=False, blank=False)
    Leave_Type = models.CharField(max_length=6, choices=LEAVE_TYPES)
    Start_Date = models.DateField(db_index=True)
    End_Date = models.DateField()
    Status = models.CharField(max_length=10, choices=STATUS_TYPES, default='PENDING', db_index=True)
    Applied_On = models.DateTimeField(auto_now_add=True)
    
    # New field for tracking who cancelled (for audit)
    Cancelled_By = models.CharField(max_length=50, blank=True, null=True)
    Cancelled_On = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.Employee_Name} - {self.Leave_Type} ({self.Status})"
    
    @property
    def is_editable(self):
        """Check if leave can be edited (only PENDING)"""
        return self.Status == 'PENDING'
    
    @property
    def is_cancellable(self):
        """Check if leave can be cancelled (only PENDING or APPROVED)"""
        return self.Status in ['PENDING', 'APPROVED']
