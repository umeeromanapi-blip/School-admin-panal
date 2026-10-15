from django.contrib import admin
from .models import AttendanceRecord


@admin.register(AttendanceRecord)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'status', 'marked_by')
    search_fields = ('student__student_name', 'student__admission_number')
    list_filter = ('status', 'date')
    ordering = ('-date',)
