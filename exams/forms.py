from django import forms
from django.core.exceptions import ValidationError
from .models import Exam, Subject, ExamSchedule, Mark
from students.models import Student
from teachers.models import Teacher


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'code', 'class_grade', 'teacher', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Mathematics', 'id': 'id_subject_name'}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. MATH-101', 'id': 'id_subject_code'}),
            'class_grade': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Class 8 or All', 'id': 'id_class_grade'}),
            'teacher': forms.Select(attrs={'class': 'form-control', 'id': 'id_teacher'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Course syllabus / description', 'id': 'id_description'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['teacher'].queryset = Teacher.objects.filter(status__iexact='Active').order_by('full_name')
        self.fields['teacher'].required = False
        self.fields['teacher'].empty_label = "-- Select Teacher (Optional) --"


class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ['name', 'exam_type', 'academic_year', 'term', 'start_date', 'end_date', 'is_published', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Midterm Examination 2026', 'id': 'id_exam_name'}),
            'exam_type': forms.Select(attrs={'class': 'form-control', 'id': 'id_exam_type'}),
            'academic_year': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '2025-2026', 'id': 'id_academic_year'}),
            'term': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. First Term', 'id': 'id_term'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'id': 'id_start_date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'id': 'id_end_date'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'id_is_published'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Instructions, guidelines for students...', 'id': 'id_description'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('start_date')
        end = cleaned_data.get('end_date')
        if start and end and end < start:
            raise ValidationError({'end_date': 'End date cannot be earlier than start date.'})
        return cleaned_data


class ExamScheduleForm(forms.ModelForm):
    class Meta:
        model = ExamSchedule
        fields = ['exam', 'subject', 'student_class', 'exam_date', 'start_time', 'end_time', 'room_number', 'total_marks', 'passing_marks']
        widgets = {
            'exam': forms.Select(attrs={'class': 'form-control', 'id': 'id_exam'}),
            'subject': forms.Select(attrs={'class': 'form-control', 'id': 'id_subject'}),
            'student_class': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Class 8', 'id': 'id_student_class'}),
            'exam_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'id': 'id_exam_date'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time', 'id': 'id_start_time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time', 'id': 'id_end_time'}),
            'room_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Hall A / Room 204', 'id': 'id_room_number'}),
            'total_marks': forms.NumberInput(attrs={'class': 'form-control', 'id': 'id_total_marks', 'step': '0.5'}),
            'passing_marks': forms.NumberInput(attrs={'class': 'form-control', 'id': 'id_passing_marks', 'step': '0.5'}),
        }


class MarkForm(forms.ModelForm):
    class Meta:
        model = Mark
        fields = ['exam', 'student', 'subject', 'marks_obtained', 'total_marks', 'remarks']
        widgets = {
            'exam': forms.Select(attrs={'class': 'form-control', 'id': 'id_exam'}),
            'student': forms.Select(attrs={'class': 'form-control', 'id': 'id_student'}),
            'subject': forms.Select(attrs={'class': 'form-control', 'id': 'id_subject'}),
            'marks_obtained': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.5', 'id': 'id_marks_obtained'}),
            'total_marks': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '100.00', 'step': '0.5', 'id': 'id_total_marks'}),
            'remarks': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional teacher remarks...', 'id': 'id_remarks'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['student'].queryset = Student.objects.all().order_by('student_name')
        self.fields['student'].label_from_instance = lambda s: f"{s.student_name} ({s.student_class} - {s.admission_number})"
        self.fields['subject'].queryset = Subject.objects.all().order_by('name')
        self.fields['exam'].queryset = Exam.objects.all().order_by('-start_date')

    def clean(self):
        cleaned_data = super().clean()
        obtained = cleaned_data.get('marks_obtained')
        total = cleaned_data.get('total_marks')
        if obtained is not None and total is not None:
            if obtained < 0:
                raise ValidationError({'marks_obtained': 'Marks cannot be negative.'})
            if obtained > total:
                raise ValidationError({'marks_obtained': f'Marks obtained cannot exceed total marks ({total}).'})
        return cleaned_data
