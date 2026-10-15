from django.db import models


class Teacher(models.Model):
    """
    Teacher / staff member record. Linked to students via student_class for
    attendance and reporting purposes.
    """
    DEPARTMENT_CHOICES = [
        ('Science', 'Science'),
        ('Mathematics', 'Mathematics'),
        ('English', 'English'),
        ('Urdu', 'Urdu'),
        ('Social Studies', 'Social Studies'),
        ('Islamic Studies', 'Islamic Studies'),
        ('Computer Science', 'Computer Science'),
        ('Arts', 'Arts'),
        ('Physical Education', 'Physical Education'),
        ('Other', 'Other'),
    ]
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('On Leave', 'On Leave'),
        ('Retired', 'Retired'),
        ('Terminated', 'Terminated'),
    ]

    employee_id = models.CharField(
        max_length=30, unique=True, verbose_name='Employee ID'
    )
    full_name = models.CharField(max_length=150, verbose_name='Full Name')
    email = models.EmailField(max_length=254, blank=True, verbose_name='Email Address')
    phone = models.CharField(max_length=20, verbose_name='Contact Number')
    department = models.CharField(
        max_length=60, choices=DEPARTMENT_CHOICES, default='Other', verbose_name='Department'
    )
    subject = models.CharField(max_length=100, verbose_name='Subject / Specialisation')
    assigned_class = models.CharField(
        max_length=100, blank=True, verbose_name='Assigned Class(es)',
        help_text='Comma-separated class names e.g. Class 8-A, Class 9-B'
    )
    qualification = models.CharField(max_length=150, blank=True, verbose_name='Qualification')
    date_joined = models.DateField(verbose_name='Joining Date')
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='Active', verbose_name='Employment Status'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Teacher'
        verbose_name_plural = 'Teachers'

    def __str__(self):
        return f"{self.full_name} ({self.employee_id})"

    def clean(self):
        super().clean()
        if self.full_name:
            self.full_name = self.full_name.strip()
        if self.employee_id:
            self.employee_id = self.employee_id.strip().upper()
        if self.phone:
            self.phone = self.phone.strip()
