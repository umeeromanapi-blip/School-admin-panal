from django.contrib import admin
from .models import FeeRecord


@admin.register(FeeRecord)
class FeeRecordAdmin(admin.ModelAdmin):
    list_display = ('student', 'fee_type', 'amount_due', 'amount_paid', 'status', 'due_date')
    search_fields = ('student__student_name', 'student__admission_number')
    list_filter = ('status', 'fee_type', 'due_date')
    ordering = ('-due_date',)
