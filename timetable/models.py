from django.db import models
from django.core.exceptions import ValidationError


class Period(models.Model):
    """Bell schedule period slot"""
    period_number = models.PositiveIntegerField(unique=True, verbose_name="Period #")
    name = models.CharField(max_length=60, verbose_name="Period Name", help_text="e.g. Period 1, Break, Lunch")
    start_time = models.TimeField(verbose_name="Start Time")
    end_time = models.TimeField(verbose_name="End Time")
    is_break = models.BooleanField(default=False, verbose_name="Break / Recess Slot")

    class Meta:
        ordering = ['period_number', 'start_time']
        verbose_name = "Class Period"
        verbose_name_plural = "Class Periods"

    def __str__(self):
        return f"Period {self.period_number}: {self.name} ({self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')})"

    def clean(self):
        super().clean()
        if self.start_time and self.end_time and self.end_time <= self.start_time:
            raise ValidationError({'end_time': 'End time must be later than start time.'})


class TimetableEntry(models.Model):
    """Weekly schedule slot mapping a class, day, and period to a subject, teacher, and room"""
    DAY_CHOICES = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
    ]

    student_class = models.CharField(max_length=50, verbose_name="Class / Grade")
    day_of_week = models.CharField(max_length=15, choices=DAY_CHOICES, verbose_name="Day of Week")
    period = models.ForeignKey(Period, on_delete=models.CASCADE, related_name='timetable_entries', verbose_name="Period")
    subject = models.ForeignKey('exams.Subject', on_delete=models.CASCADE, related_name='timetable_entries', verbose_name="Subject")
    teacher = models.ForeignKey('teachers.Teacher', on_delete=models.SET_NULL, null=True, blank=True, related_name='timetable_slots', verbose_name="Assigned Teacher")
    room_number = models.CharField(max_length=30, blank=True, default="Room 101", verbose_name="Classroom / Hall")
    academic_year = models.CharField(max_length=20, default="2025-2026", verbose_name="Academic Year")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['day_of_week', 'period__period_number']
        unique_together = ('student_class', 'day_of_week', 'period')
        verbose_name = "Timetable Entry"
        verbose_name_plural = "Timetable Entries"

    def __str__(self):
        return f"{self.student_class} - {self.day_of_week} {self.period.name}: {self.subject.name}"

    def clean(self):
        super().clean()
        # Clash detection: Check if the assigned teacher is already booked elsewhere on the same day and period
        if self.teacher and self.period and self.day_of_week:
            clash_teacher = TimetableEntry.objects.filter(
                teacher=self.teacher,
                day_of_week=self.day_of_week,
                period=self.period
            ).exclude(pk=self.pk)
            if clash_teacher.exists():
                existing = clash_teacher.first()
                raise ValidationError({
                    'teacher': f"Teacher clash! {self.teacher.full_name} is already assigned to {existing.student_class} on {self.day_of_week} during {self.period.name}."
                })
