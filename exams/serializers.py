from rest_framework import serializers
from .models import Subject, Exam, ExamSchedule, Mark


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name', 'code', 'class_grade', 'teacher', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']


class ExamSerializer(serializers.ModelSerializer):
    exam_type_display = serializers.CharField(source='get_exam_type_display', read_only=True)

    class Meta:
        model = Exam
        fields = [
            'id',
            'name',
            'exam_type',
            'exam_type_display',
            'academic_year',
            'term',
            'start_date',
            'end_date',
            'is_published',
            'description',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class MarkSerializer(serializers.ModelSerializer):
    student_name = serializers.ReadOnlyField(source='student.student_name')
    admission_number = serializers.ReadOnlyField(source='student.admission_number')
    subject_name = serializers.ReadOnlyField(source='subject.name')
    exam_name = serializers.ReadOnlyField(source='exam.name')

    class Meta:
        model = Mark
        fields = [
            'id',
            'student',
            'student_name',
            'admission_number',
            'exam',
            'exam_name',
            'subject',
            'subject_name',
            'marks_obtained',
            'max_marks',
            'grade',
            'remarks',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'grade', 'created_at', 'updated_at']
