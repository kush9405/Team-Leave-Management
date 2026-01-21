from django.db import models

# Create your models here.
class Leave_Record(models.Model):
    LEAVE_TYPES = (
        ('SICK', 'Sick Leave'),
        ('CASUAL', 'Casual Leave'),
        ('EARNED', 'Earned Leave'),
    )
    STATUS_TYPES=(
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    )

    Employee_Name = models.CharField(max_length=50, null=False, blank=False,)
    Leave_Type = models.CharField(max_length=6, choices=LEAVE_TYPES)
    Start_Date = models.DateField(db_index=True)
    End_Date = models.DateField()
    Status = models.CharField(max_length=8, choices=STATUS_TYPES, default='PENDING', db_index=True)
    Applied_On = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.Employee_Name + " - " + self.Leave_Type