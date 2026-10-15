from django.db import models
from django.utils import timezone


class Announcement(models.Model):
    """School announcements & notice board notices"""
    AUDIENCE_CHOICES = [
        ('all', 'All Students & Staff'),
        ('students', 'Students Only'),
        ('teachers', 'Teachers Only'),
        ('parents', 'Parents Only'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High Priority'),
        ('urgent', 'Urgent / Alert'),
    ]

    CATEGORY_CHOICES = [
        ('general', 'General Notice'),
        ('academic', 'Academic / Exams'),
        ('holiday', 'Holidays & Closures'),
        ('sports', 'Sports & Events'),
        ('fees', 'Fee & Finance Notice'),
    ]

    title = models.CharField(max_length=200, verbose_name="Notice Title")
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='general', verbose_name="Category")
    content = models.TextField(verbose_name="Notice Content")
    audience = models.CharField(max_length=30, choices=AUDIENCE_CHOICES, default='all', verbose_name="Target Audience")
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='normal', verbose_name="Priority Level")
    is_pinned = models.BooleanField(default=False, verbose_name="Pin to Top")
    is_active = models.BooleanField(default=True, verbose_name="Active")
    published_date = models.DateField(default=timezone.now, verbose_name="Publish Date")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_pinned', '-published_date', '-created_at']
        verbose_name = "Announcement"
        verbose_name_plural = "Announcements"

    def __str__(self):
        return f"[{self.get_priority_display()}] {self.title}"

    def clean(self):
        super().clean()
        if self.title:
            self.title = self.title.strip()
