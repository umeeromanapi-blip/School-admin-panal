from rest_framework import serializers
from .models import Teacher


class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = [
            'id',
            'employee_id',
            'full_name',
            'email',
            'phone',
            'department',
            'subject',
            'assigned_class',
            'qualification',
            'date_joined',
            'status',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_employee_id(self, value):
        val = value.strip().upper() if value else ''
        if not val:
            raise serializers.ValidationError("Employee ID is required.")
        return val

    def validate_full_name(self, value):
        val = value.strip() if value else ''
        if not val:
            raise serializers.ValidationError("Full name is required.")
        return val
