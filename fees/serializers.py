from rest_framework import serializers
from .models import FeeRecord


class FeeRecordSerializer(serializers.ModelSerializer):
    student_name = serializers.ReadOnlyField(source='student.student_name')
    admission_number = serializers.ReadOnlyField(source='student.admission_number')
    student_class = serializers.ReadOnlyField(source='student.student_class')

    class Meta:
        model = FeeRecord
        fields = [
            'id',
            'student',
            'student_name',
            'admission_number',
            'student_class',
            'fee_type',
            'amount_due',
            'amount_paid',
            'status',
            'month',
            'year',
            'due_date',
            'payment_date',
            'remarks',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
