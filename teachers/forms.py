import re
from django import forms
from django.core.exceptions import ValidationError
from .models import Teacher


class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = [
            'employee_id', 'full_name', 'email', 'phone',
            'department', 'subject', 'assigned_class',
            'qualification', 'date_joined', 'status',
        ]
        widgets = {
            'employee_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. TCH-001', 'id': 'id_employee_id'}),
            'full_name':   forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Mr. Ahsan Ali', 'id': 'id_full_name'}),
            'email':       forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'teacher@school.edu.pk', 'id': 'id_email'}),
            'phone':       forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 03001234567', 'type': 'tel', 'id': 'id_phone'}),
            'department':  forms.Select(attrs={'class': 'form-control', 'id': 'id_department'}),
            'subject':     forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Physics', 'id': 'id_subject'}),
            'assigned_class': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Class 9-A, Class 10-B', 'id': 'id_assigned_class'}),
            'qualification': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. M.Sc Physics, B.Ed', 'id': 'id_qualification'}),
            'date_joined': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'id': 'id_date_joined'}),
            'status':      forms.Select(attrs={'class': 'form-control', 'id': 'id_status'}),
        }
        error_messages = {
            'employee_id': {'required': 'Employee ID is required.', 'unique': 'This Employee ID is already in use.'},
            'full_name':   {'required': 'Full name is required.'},
            'phone':       {'required': 'Contact number is required.'},
            'subject':     {'required': 'Subject is required.'},
            'date_joined': {'required': 'Joining date is required.'},
        }

    def clean_employee_id(self):
        emp_id = self.cleaned_data.get('employee_id', '').strip()
        if not emp_id:
            raise ValidationError('Employee ID cannot be empty.')
        qs = Teacher.objects.filter(employee_id__iexact=emp_id)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError('A teacher with this Employee ID already exists.')
        return emp_id.upper()

    def clean_full_name(self):
        name = self.cleaned_data.get('full_name', '').strip()
        if not name:
            raise ValidationError('Full name cannot be empty or whitespace.')
        return name

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        if not phone:
            raise ValidationError('Contact number is required.')
        if not re.search(r'\d', phone):
            raise ValidationError('Contact number must contain valid digits.')
        if not re.match(r'^[0-9+\-\s()]+$', phone):
            raise ValidationError('Contact number can only contain digits, +, -, and parentheses.')
        return phone
