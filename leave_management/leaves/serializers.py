from rest_framework import serializers
from .models import Leave_Record

class LeaveRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model=Leave_Record
        fields='__all__'

        def validate(self,data):
            if data['Applied_On']>=data['Start_Date']:
                raise serializers.ValidationError("Sorry!! You should have applied for the leave beforehand")
            return data
        def validate_date(self,data):
            if data['Start_Date']>data['End_Date']:
                raise serializers.ValidationError("End Date must be after Start Date")
            return data
        def validate_Employee_Name(self,value):
            if not value.replace(" ","").isalpha():
                raise serializers.ValidationError("Employee Name must contain only alphabetic characters and spaces")
            return value
        def validate_Leave_Type(self,value):
            leave_types=[choice[0] for choice in Leave_Record.LEAVE_TYPES]
            if value not in leave_types:
                raise serializers.ValidationError(f"Leave Type must be one of {', '.join(leave_types)}")
            return value
        def validate_Status(self,value):
            status_types=[choice[0] for choice in Leave_Record.STATUS_TYPES]
            if value not in status_types:
                raise serializers.ValidationError(f"Status must be one of {', '.join(status_types)}")
            return value
