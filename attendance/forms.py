from django import forms
from django.core.exceptions import ValidationError
from .models import AttendanceRecord
from students.models import Student
import datetime


class AttendanceDateForm(forms.Form):
    """Select date and class to mark bulk attendance."""
    date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'id': 'id_date'}),
        initial=datetime.date.today,
        label='Attendance Date',
    )
    student_class = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_student_class'}),
        label='Select Class',
    )

    def __init__(self, *args, **kwargs):
        class_choices = kwargs.pop('class_choices', [])
        super().__init__(*args, **kwargs)
        self.fields['student_class'].choices = [('', '--- Select Class ---')] + list(class_choices)

    def clean_date(self):
        d = self.cleaned_data.get('date')
        if d and d > datetime.date.today():
            raise ValidationError('Cannot mark attendance for a future date.')
        return d


class AttendanceRecordForm(forms.ModelForm):
    class Meta:
        model = AttendanceRecord
        fields = ['student', 'date', 'status', 'remarks', 'marked_by']
        widgets = {
            'student':   forms.Select(attrs={'class': 'form-control', 'id': 'id_student'}),
            'date':      forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'id': 'id_date'}),
            'status':    forms.Select(attrs={'class': 'form-control', 'id': 'id_status'}),
            'remarks':   forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional reason or note', 'id': 'id_remarks'}),
            'marked_by': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teacher name or ID', 'id': 'id_marked_by'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['student'].queryset = Student.objects.all().order_by('student_name')
        self.fields['student'].label_from_instance = lambda s: f"{s.student_name} ({s.admission_number} — {s.student_class})"
