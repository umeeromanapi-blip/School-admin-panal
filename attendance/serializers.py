from rest_framework import serializers
from .models import AttendanceRecord
from students.serializers import StudentSerializer


class AttendanceRecordSerializer(serializers.ModelSerializer):
    student_name = serializers.ReadOnlyField(source='student.student_name')
    admission_number = serializers.ReadOnlyField(source='student.admission_number')
    student_class = serializers.ReadOnlyField(source='student.student_class')

    class Meta:
        model = AttendanceRecord
        fields = [
            'id',
            'student',
            'student_name',
            'admission_number',
            'student_class',
            'date',
            'status',
            'remarks',
            'marked_by',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
