from django import forms
from django.core.exceptions import ValidationError
from .models import Period, TimetableEntry
from exams.models import Subject
from teachers.models import Teacher
from students.models import Student


class PeriodForm(forms.ModelForm):
    class Meta:
        model = Period
        fields = ['period_number', 'name', 'start_time', 'end_time', 'is_break']
        widgets = {
            'period_number': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'id': 'id_period_number'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Period 1, Recess, Lunch', 'id': 'id_name'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time', 'id': 'id_start_time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time', 'id': 'id_end_time'}),
            'is_break': forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'id_is_break'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('start_time')
        end = cleaned_data.get('end_time')
        if start and end and end <= start:
            raise ValidationError({'end_time': 'End time must be after start time.'})
        return cleaned_data


class TimetableEntryForm(forms.ModelForm):
    class Meta:
        model = TimetableEntry
        fields = ['student_class', 'day_of_week', 'period', 'subject', 'teacher', 'room_number', 'academic_year']
        widgets = {
            'student_class': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Class 8', 'id': 'id_student_class'}),
            'day_of_week': forms.Select(attrs={'class': 'form-control', 'id': 'id_day_of_week'}),
            'period': forms.Select(attrs={'class': 'form-control', 'id': 'id_period'}),
            'subject': forms.Select(attrs={'class': 'form-control', 'id': 'id_subject'}),
            'teacher': forms.Select(attrs={'class': 'form-control', 'id': 'id_teacher'}),
            'room_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Room 101, Lab 2', 'id': 'id_room_number'}),
            'academic_year': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '2025-2026', 'id': 'id_academic_year'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['teacher'].queryset = Teacher.objects.filter(status__iexact='Active').order_by('full_name')
        self.fields['teacher'].required = False
        self.fields['teacher'].empty_label = "-- Select Teacher (Optional) --"
        self.fields['subject'].queryset = Subject.objects.all().order_by('name')
        self.fields['period'].queryset = Period.objects.all().order_by('period_number')
