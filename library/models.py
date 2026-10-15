from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal
import datetime


class Book(models.Model):
    """Library book catalog inventory"""
    CATEGORY_CHOICES = [
        ('Science', 'Science & Technology'),
        ('Literature', 'Literature & English'),
        ('Mathematics', 'Mathematics & Logic'),
        ('History', 'History & Social Studies'),
        ('Islamic', 'Islamic & Religious Studies'),
        ('Computer', 'Computer Science & AI'),
        ('General', 'General Reference & Encyclopedias'),
    ]

    title = models.CharField(max_length=200, verbose_name="Book Title")
    isbn = models.CharField(max_length=40, unique=True, verbose_name="ISBN / Catalog ID")
    author = models.CharField(max_length=150, verbose_name="Author")
    category = models.CharField(max_length=40, choices=CATEGORY_CHOICES, default='General', verbose_name="Category")
    publisher = models.CharField(max_length=150, blank=True, verbose_name="Publisher")
    edition = models.CharField(max_length=50, blank=True, default="1st Edition", verbose_name="Edition")
    total_copies = models.PositiveIntegerField(default=1, verbose_name="Total Copies")
    available_copies = models.PositiveIntegerField(default=1, verbose_name="Available Copies")
    rack_location = models.CharField(max_length=50, blank=True, default="Shelf A-1", verbose_name="Rack / Shelf Location")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']
        verbose_name = "Library Book"
        verbose_name_plural = "Library Books"

    def __str__(self):
        return f"{self.title} by {self.author} ({self.isbn})"

    def clean(self):
        super().clean()
        if self.title:
            self.title = self.title.strip()
        if self.isbn:
            self.isbn = self.isbn.strip().upper()
        if self.available_copies > self.total_copies:
            raise ValidationError({'available_copies': 'Available copies cannot exceed total copies.'})


class BookIssue(models.Model):
    """Borrowing and return transaction for library books"""
    BORROWER_TYPE_CHOICES = [
        ('student', 'Student'),
        ('teacher', 'Teacher'),
    ]

    STATUS_CHOICES = [
        ('Issued', 'Active / Borrowed'),
        ('Returned', 'Returned'),
        ('Overdue', 'Overdue'),
    ]

    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='borrowing_records', verbose_name="Book")
    borrower_type = models.CharField(max_length=10, choices=BORROWER_TYPE_CHOICES, default='student', verbose_name="Borrower Type")
    student = models.ForeignKey('students.Student', on_delete=models.SET_NULL, null=True, blank=True, related_name='borrowed_books', verbose_name="Student")
    teacher = models.ForeignKey('teachers.Teacher', on_delete=models.SET_NULL, null=True, blank=True, related_name='borrowed_books', verbose_name="Teacher")
    issue_date = models.DateField(default=timezone.now, verbose_name="Issue Date")
    due_date = models.DateField(verbose_name="Due Date")
    return_date = models.DateField(null=True, blank=True, verbose_name="Actual Return Date")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Issued', verbose_name="Loan Status")
    fine_amount = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('0.00'), verbose_name="Overdue Fine (PKR)")
    remarks = models.CharField(max_length=200, blank=True, verbose_name="Condition / Notes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-issue_date', '-created_at']
        verbose_name = "Book Loan Record"
        verbose_name_plural = "Book Loan Records"

    def __str__(self):
        borrower = self.student.student_name if self.student else (self.teacher.full_name if self.teacher else 'Unknown')
        return f"{self.book.title} issued to {borrower} (Due: {self.due_date})"

    @property
    def borrower_name(self):
        if self.borrower_type == 'student' and self.student:
            return f"{self.student.student_name} ({self.student.student_class} - {self.student.admission_number})"
        elif self.borrower_type == 'teacher' and self.teacher:
            return f"{self.teacher.full_name} ({self.teacher.department})"
        return "Unknown"

    @property
    def is_currently_overdue(self):
        if self.status != 'Returned' and self.due_date:
            return datetime.date.today() > self.due_date
        return False

    def calculate_fine(self, rate_per_day=Decimal('10.00')):
        if self.is_currently_overdue:
            ref_date = self.return_date or datetime.date.today()
            if ref_date > self.due_date:
                days = (ref_date - self.due_date).days
                return Decimal(days) * rate_per_day
        return Decimal('0.00')

    def clean(self):
        super().clean()
        if self.borrower_type == 'student' and not self.student:
            raise ValidationError({'student': 'Please select a student for this loan.'})
        if self.borrower_type == 'teacher' and not self.teacher:
            raise ValidationError({'teacher': 'Please select a teacher for this loan.'})
        if self.issue_date and self.due_date and self.due_date < self.issue_date:
            raise ValidationError({'due_date': 'Due date cannot precede issue date.'})
