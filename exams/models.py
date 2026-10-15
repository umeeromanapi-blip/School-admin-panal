from django.db import models
from django.core.exceptions import ValidationError
from decimal import Decimal


class Subject(models.Model):
    """Subject/Course taught at school"""
    name = models.CharField(max_length=100, verbose_name="Subject Name")
    code = models.CharField(max_length=30, unique=True, verbose_name="Subject Code")
    class_grade = models.CharField(max_length=50, blank=True, verbose_name="Target Class/Grade", help_text="e.g. Class 8 or All")
    teacher = models.ForeignKey(
        'teachers.Teacher',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_subjects',
        verbose_name="Assigned Teacher"
    )
    description = models.TextField(blank=True, verbose_name="Subject Description")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Subject"
        verbose_name_plural = "Subjects"

    def __str__(self):
        return f"{self.name} ({self.code})"

    def clean(self):
        super().clean()
        if self.name:
            self.name = self.name.strip()
        if self.code:
            self.code = self.code.strip().upper()


class Exam(models.Model):
    """Examination schedule & event"""
    EXAM_TYPE_CHOICES = [
        ('midterm', 'Midterm Examination'),
        ('final', 'Final Examination'),
        ('quiz', 'Monthly Assessment / Quiz'),
        ('practical', 'Practical Lab Exam'),
        ('annual', 'Annual Board Exam'),
    ]

    name = models.CharField(max_length=150, verbose_name="Exam Name")
    exam_type = models.CharField(max_length=30, choices=EXAM_TYPE_CHOICES, default='midterm', verbose_name="Exam Type")
    academic_year = models.CharField(max_length=20, default="2025-2026", verbose_name="Academic Year")
    term = models.CharField(max_length=50, default="First Term", verbose_name="Term / Semester")
    start_date = models.DateField(verbose_name="Start Date")
    end_date = models.DateField(verbose_name="End Date")
    is_published = models.BooleanField(default=True, verbose_name="Published / Active")
    description = models.TextField(blank=True, verbose_name="Instructions / Details")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_date']
        verbose_name = "Exam"
        verbose_name_plural = "Exams"

    def __str__(self):
        return f"{self.name} ({self.academic_year})"

    def clean(self):
        super().clean()
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValidationError({'end_date': 'End date cannot precede start date.'})


class ExamSchedule(models.Model):
    """Date & time schedule per subject for an exam"""
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='schedules')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='schedules')
    student_class = models.CharField(max_length=50, verbose_name="Class / Grade")
    exam_date = models.DateField(verbose_name="Exam Date")
    start_time = models.TimeField(verbose_name="Start Time")
    end_time = models.TimeField(verbose_name="End Time")
    room_number = models.CharField(max_length=30, blank=True, verbose_name="Room / Hall")
    total_marks = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('100.00'), verbose_name="Total Marks")
    passing_marks = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('40.00'), verbose_name="Passing Marks")

    class Meta:
        ordering = ['exam_date', 'start_time']
        unique_together = ('exam', 'subject', 'student_class')
        verbose_name = "Exam Schedule"
        verbose_name_plural = "Exam Schedules"

    def __str__(self):
        return f"{self.exam.name} - {self.subject.name} ({self.student_class})"


class Mark(models.Model):
    """Student Mark/Result in an Exam & Subject"""
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='marks')
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='marks')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='marks')
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Marks Obtained")
    total_marks = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('100.00'), verbose_name="Total Marks")
    grade = models.CharField(max_length=5, blank=True, verbose_name="Grade")
    remarks = models.CharField(max_length=200, blank=True, verbose_name="Remarks / Comments")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-exam__start_date', 'student__student_name', 'subject__name']
        unique_together = ('exam', 'student', 'subject')
        verbose_name = "Exam Mark"
        verbose_name_plural = "Exam Marks"

    def __str__(self):
        return f"{self.student.student_name} - {self.subject.name}: {self.marks_obtained}/{self.total_marks}"

    @property
    def percentage(self):
        if self.total_marks and self.total_marks > 0:
            return round((float(self.marks_obtained) / float(self.total_marks)) * 100, 1)
        return 0.0

    @property
    def is_passed(self):
        return self.percentage >= 40.0

    def compute_grade(self):
        pct = self.percentage
        if pct >= 90:
            return "A+"
        elif pct >= 80:
            return "A"
        elif pct >= 70:
            return "B"
        elif pct >= 60:
            return "C"
        elif pct >= 50:
            return "D"
        elif pct >= 40:
            return "E"
        else:
            return "F"

    def clean(self):
        super().clean()
        if self.marks_obtained is not None and self.total_marks is not None:
            if self.marks_obtained < 0:
                raise ValidationError({'marks_obtained': 'Marks obtained cannot be negative.'})
            if self.marks_obtained > self.total_marks:
                raise ValidationError({'marks_obtained': f'Marks obtained cannot exceed total marks ({self.total_marks}).'})

    def save(self, *args, **kwargs):
        self.grade = self.compute_grade()
        super().save(*args, **kwargs)
