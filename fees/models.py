from django.db import models
from students.models import Student


class FeeRecord(models.Model):
    """
    Fee payment record for a student per month/term.
    Tracks amount, paid status, and due date.
    """
    FEE_TYPE_CHOICES = [
        ('Monthly Tuition', 'Monthly Tuition'),
        ('Admission Fee', 'Admission Fee'),
        ('Exam Fee', 'Exam Fee'),
        ('Library Fee', 'Library Fee'),
        ('Transport Fee', 'Transport Fee'),
        ('Activity Fee', 'Activity Fee'),
        ('Other', 'Other'),
    ]
    STATUS_CHOICES = [
        ('Paid', 'Paid'),
        ('Unpaid', 'Unpaid'),
        ('Partial', 'Partial'),
        ('Waived', 'Waived'),
    ]
    MONTH_CHOICES = [
        (1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
        (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
        (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December'),
    ]

    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name='fee_records',
        verbose_name='Student'
    )
    fee_type = models.CharField(
        max_length=60, choices=FEE_TYPE_CHOICES, default='Monthly Tuition',
        verbose_name='Fee Type'
    )
    amount_due = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name='Amount Due (PKR)'
    )
    amount_paid = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name='Amount Paid (PKR)'
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='Unpaid', verbose_name='Payment Status'
    )
    month = models.IntegerField(
        choices=MONTH_CHOICES, verbose_name='Month', null=True, blank=True
    )
    year = models.IntegerField(verbose_name='Year', null=True, blank=True)
    due_date = models.DateField(verbose_name='Due Date')
    payment_date = models.DateField(null=True, blank=True, verbose_name='Payment Date')
    remarks = models.TextField(blank=True, verbose_name='Remarks / Notes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-due_date', '-created_at']
        verbose_name = 'Fee Record'
        verbose_name_plural = 'Fee Records'

    def __str__(self):
        return f"{self.student.student_name} — {self.fee_type} ({self.get_status_display()})"

    @property
    def balance(self):
        return self.amount_due - self.amount_paid
