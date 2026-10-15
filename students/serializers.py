from rest_framework import serializers
from .models import Student


class StudentSerializer(serializers.ModelSerializer):
    """
    Serializer for Student model matching API Specification Sec. 4 & 6.
    Enforces validation constraints, uppercase admission numbers,
    and text-formatted contact numbers.
    """
    class Meta:
        model = Student
        fields = [
            'id',
            'student_name',
            'admission_number',
            'student_class',
            'contact_number',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_student_name(self, value):
        val = value.strip() if value else ''
        if not val:
            raise serializers.ValidationError("Student name is required.")
        if len(val) > 150:
            raise serializers.ValidationError("Student name must not exceed 150 characters.")
        return val

    def validate_admission_number(self, value):
        val = value.strip().upper() if value else ''
        if not val:
            raise serializers.ValidationError("Admission number is required.")
        if len(val) > 30:
            raise serializers.ValidationError("Admission number must not exceed 30 characters.")
        return val

    def validate_student_class(self, value):
        val = value.strip() if value else ''
        if not val:
            raise serializers.ValidationError("Class / Grade is required.")
        if len(val) > 50:
            raise serializers.ValidationError("Class name must not exceed 50 characters.")
        return val

    def validate_contact_number(self, value):
        val = value.strip() if value else ''
        if not val:
            raise serializers.ValidationError("Contact number is required.")
        if len(val) > 20:
            raise serializers.ValidationError("Contact number must not exceed 20 characters.")
        return val
