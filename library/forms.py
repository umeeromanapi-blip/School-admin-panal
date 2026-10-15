from django import forms
from django.core.exceptions import ValidationError
from .models import Book, BookIssue
from students.models import Student
from teachers.models import Teacher
from decimal import Decimal


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'isbn', 'author', 'category', 'publisher', 'edition', 'total_copies', 'available_copies', 'rack_location']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Clean Code: A Handbook of Agile Software Craftsmanship', 'id': 'id_title'}),
            'isbn': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. ISBN-978-0132350884', 'id': 'id_isbn'}),
            'author': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Robert C. Martin', 'id': 'id_author'}),
            'category': forms.Select(attrs={'class': 'form-control', 'id': 'id_category'}),
            'publisher': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Prentice Hall', 'id': 'id_publisher'}),
            'edition': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 1st Edition', 'id': 'id_edition'}),
            'total_copies': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'id': 'id_total_copies'}),
            'available_copies': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'id': 'id_available_copies'}),
            'rack_location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Shelf CS-03', 'id': 'id_rack_location'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        total = cleaned_data.get('total_copies')
        avail = cleaned_data.get('available_copies')
        if total is not None and avail is not None and avail > total:
            raise ValidationError({'available_copies': f'Available copies ({avail}) cannot exceed total copies ({total}).'})
        return cleaned_data


class BookIssueForm(forms.ModelForm):
    class Meta:
        model = BookIssue
        fields = ['book', 'borrower_type', 'student', 'teacher', 'issue_date', 'due_date', 'remarks']
        widgets = {
            'book': forms.Select(attrs={'class': 'form-control', 'id': 'id_book'}),
            'borrower_type': forms.Select(attrs={'class': 'form-control', 'id': 'id_borrower_type'}),
            'student': forms.Select(attrs={'class': 'form-control', 'id': 'id_student'}),
            'teacher': forms.Select(attrs={'class': 'form-control', 'id': 'id_teacher'}),
            'issue_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'id': 'id_issue_date'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'id': 'id_due_date'}),
            'remarks': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional condition notes...', 'id': 'id_remarks'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['book'].queryset = Book.objects.filter(available_copies__gt=0).order_by('title')
        self.fields['book'].label_from_instance = lambda b: f"{b.title} (Avail: {b.available_copies}) - {b.isbn}"
        self.fields['student'].queryset = Student.objects.all().order_by('student_name')
        self.fields['student'].label_from_instance = lambda s: f"{s.student_name} ({s.student_class} - {s.admission_number})"
        self.fields['student'].required = False
        self.fields['teacher'].queryset = Teacher.objects.filter(status__iexact='Active').order_by('full_name')
        self.fields['teacher'].label_from_instance = lambda t: f"{t.full_name} ({t.department})"
        self.fields['teacher'].required = False


class BookReturnForm(forms.Form):
    return_date = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'id': 'id_return_date'}))
    fine_amount = forms.DecimalField(max_digits=6, decimal_places=2, required=False, initial=Decimal('0.00'), widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '5.00', 'id': 'id_fine_amount'}))
    remarks = forms.CharField(max_length=200, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Book condition upon return...', 'id': 'id_remarks'}))
