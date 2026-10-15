from django.db import models
from students.models import Student


class AttendanceRecord(models.Model):
    """
    Daily attendance record per student.
    Supports Present, Absent, Late, and Leave statuses.
    """
    STATUS_CHOICES = [
        ('Present', 'Present'),
        ('Absent', 'Absent'),
        ('Late', 'Late'),
        ('Leave', 'Leave (Excused)'),
    ]

    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name='attendance_records',
        verbose_name='Student'
    )
    date = models.DateField(verbose_name='Date')
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='Present',
        verbose_name='Attendance Status'
    )
    remarks = models.CharField(
        max_length=200, blank=True, verbose_name='Remarks',
        help_text='Optional note (e.g. sick leave, family event)'
    )
    marked_by = models.CharField(
        max_length=100, blank=True, verbose_name='Marked By',
        help_text='Teacher or staff who marked attendance'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', 'student__student_name']
        # Prevent duplicate attendance entries per student per day
        unique_together = [('student', 'date')]
        verbose_name = 'Attendance Record'
        verbose_name_plural = 'Attendance Records'

    def __str__(self):
        return f"{self.student.student_name} — {self.date} ({self.status})"
