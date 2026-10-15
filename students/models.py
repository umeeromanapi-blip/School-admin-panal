from django.db import models


class Student(models.Model):
    """
    Model representing a student record in the School Admin Panel.
    Enforces required fields, unique admission numbers, and stores
    contact numbers as text to preserve leading zeros.
    """
    student_name = models.CharField(
        max_length=150,
        verbose_name="Student Name",
        help_text="Full legal name of the student"
    )
    admission_number = models.CharField(
        max_length=30,
        unique=True,
        verbose_name="Admission Number",
        help_text="Unique institutional admission identifier"
    )
    student_class = models.CharField(
        max_length=50,
        verbose_name="Class / Grade",
        help_text="Current class or grade level"
    )
    contact_number = models.CharField(
        max_length=20,
        verbose_name="Contact Number",
        help_text="Primary guardian contact phone number"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Registered On"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Last Updated"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Student"
        verbose_name_plural = "Students"

    def __str__(self):
        return f"{self.student_name} ({self.admission_number})"

    def clean(self):
        super().clean()
        if self.student_name:
            self.student_name = self.student_name.strip()
        if self.admission_number:
            self.admission_number = self.admission_number.strip().upper()
        if self.student_class:
            self.student_class = self.student_class.strip()
        if self.contact_number:
            self.contact_number = self.contact_number.strip()
