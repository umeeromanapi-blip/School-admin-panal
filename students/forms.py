import re
from django import forms
from django.core.exceptions import ValidationError
from .models import Student


class StudentForm(forms.ModelForm):
    """
    Form for adding and updating student records with comprehensive validation,
    sanitization, and modern UI widget styling.
    """

    class Meta:
        model = Student
        fields = ['student_name', 'admission_number', 'student_class', 'contact_number']
        widgets = {
            'student_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Ali Khan',
                'autocomplete': 'name',
                'required': True,
                'id': 'id_student_name',
            }),
            'admission_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. ADM-001',
                'autocomplete': 'off',
                'required': True,
                'id': 'id_admission_number',
            }),
            'student_class': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Class 8 or Grade 10-A',
                'required': True,
                'id': 'id_student_class',
            }),
            'contact_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. 03001234567 or +923001234567',
                'type': 'tel',
                'required': True,
                'id': 'id_contact_number',
            }),
        }
        labels = {
            'student_name': 'Full Student Name',
            'admission_number': 'Admission Number / ID',
            'student_class': 'Class / Grade',
            'contact_number': 'Parent / Guardian Contact Number',
        }
        help_texts = {
            'student_name': 'Enter the student\'s legal full name.',
            'admission_number': 'A unique identifier assigned by the school.',
            'student_class': 'Grade or academic section.',
            'contact_number': 'Phone number with leading zero or country code preserved.',
        }
        error_messages = {
            'student_name': {
                'required': 'Student name is required.',
                'max_length': 'Student name cannot exceed 150 characters.',
            },
            'admission_number': {
                'required': 'Admission number is required.',
                'unique': 'A student with this admission number already exists.',
                'max_length': 'Admission number cannot exceed 30 characters.',
            },
            'student_class': {
                'required': 'Class is required.',
                'max_length': 'Class cannot exceed 50 characters.',
            },
            'contact_number': {
                'required': 'Contact number is required.',
                'max_length': 'Contact number cannot exceed 20 characters.',
            },
        }

    def clean_student_name(self):
        name = self.cleaned_data.get('student_name', '').strip()
        if not name:
            raise ValidationError('Student name cannot be empty or only spaces.')
        return name

    def clean_admission_number(self):
        adm = self.cleaned_data.get('admission_number', '').strip()
        if not adm:
            raise ValidationError('Admission number cannot be empty.')
        # Ensure uniqueness when creating or updating
        qs = Student.objects.filter(admission_number__iexact=adm)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError('A student with this admission number already exists.')
        return adm.upper()

    def clean_student_class(self):
        s_class = self.cleaned_data.get('student_class', '').strip()
        if not s_class:
            raise ValidationError('Class cannot be empty.')
        return s_class

    def clean_contact_number(self):
        contact = self.cleaned_data.get('contact_number', '').strip()
        if not contact:
            raise ValidationError('Contact number cannot be empty.')
        # Ensure contact contains at least some digits
        if not re.search(r'\d', contact):
            raise ValidationError('Contact number must contain valid digits.')
        # Basic character check (digits, spaces, hyphens, parentheses, plus sign)
        if not re.match(r'^[0-9+\-\s()]+$', contact):
            raise ValidationError('Contact number can only contain digits, +, -, and parentheses.')
        return contact
