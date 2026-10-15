from django.contrib import admin
from .models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('admission_number', 'student_name', 'student_class', 'contact_number', 'created_at')
    search_fields = ('student_name', 'admission_number', 'contact_number')
    list_filter = ('student_class', 'created_at')
    ordering = ('-created_at',)
