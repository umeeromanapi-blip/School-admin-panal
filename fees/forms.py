from django import forms
from django.core.exceptions import ValidationError
from .models import FeeRecord
from students.models import Student


class FeeRecordForm(forms.ModelForm):
    class Meta:
        model = FeeRecord
        fields = [
            'student', 'fee_type', 'amount_due', 'amount_paid',
            'status', 'month', 'year', 'due_date', 'payment_date', 'remarks',
        ]
        widgets = {
            'student':      forms.Select(attrs={'class': 'form-control', 'id': 'id_student'}),
            'fee_type':     forms.Select(attrs={'class': 'form-control', 'id': 'id_fee_type'}),
            'amount_due':   forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01', 'min': '0', 'id': 'id_amount_due'}),
            'amount_paid':  forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01', 'min': '0', 'id': 'id_amount_paid'}),
            'status':       forms.Select(attrs={'class': 'form-control', 'id': 'id_status'}),
            'month':        forms.Select(attrs={'class': 'form-control', 'id': 'id_month'}),
            'year':         forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '2026', 'min': '2000', 'max': '2100', 'id': 'id_year'}),
            'due_date':     forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'id': 'id_due_date'}),
            'payment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'id': 'id_payment_date'}),
            'remarks':      forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Optional notes...', 'id': 'id_remarks'}),
        }
        error_messages = {
            'student':    {'required': 'Please select a student.'},
            'amount_due': {'required': 'Amount due is required.'},
            'due_date':   {'required': 'Due date is required.'},
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['student'].queryset = Student.objects.all().order_by('student_name')
        self.fields['student'].label_from_instance = lambda s: f"{s.student_name} ({s.admission_number})"

    def clean_amount_due(self):
        val = self.cleaned_data.get('amount_due')
        if val is not None and val < 0:
            raise ValidationError('Amount due cannot be negative.')
        return val

    def clean_amount_paid(self):
        val = self.cleaned_data.get('amount_paid', 0)
        if val is not None and val < 0:
            raise ValidationError('Amount paid cannot be negative.')
        return val

    def clean(self):
        cleaned_data = super().clean()
        due = cleaned_data.get('amount_due')
        paid = cleaned_data.get('amount_paid', 0)
        if due is not None and paid is not None and paid > due:
            raise ValidationError('Amount paid cannot exceed amount due.')
        return cleaned_data
