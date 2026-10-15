from django.contrib import admin
from .models import Teacher


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'full_name', 'department', 'subject', 'status', 'date_joined')
    search_fields = ('full_name', 'employee_id', 'subject')
    list_filter = ('department', 'status', 'date_joined')
    ordering = ('-created_at',)
