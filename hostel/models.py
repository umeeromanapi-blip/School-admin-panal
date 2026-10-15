from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal


class Hostel(models.Model):
    """Hostel / Dormitory residence building"""
    HOSTEL_TYPE_CHOICES = [
        ('Boys', 'Boys Hostel'),
        ('Girls', 'Girls Hostel'),
        ('Faculty', 'Faculty / Staff Residency'),
    ]

    name = models.CharField(max_length=150, unique=True, verbose_name="Hostel / Hall Name")
    hostel_type = models.CharField(max_length=20, choices=HOSTEL_TYPE_CHOICES, default='Boys', verbose_name="Residency Type")
    warden_name = models.CharField(max_length=120, verbose_name="Warden / Caretaker Name")
    warden_phone = models.CharField(max_length=25, verbose_name="Warden Contact Number")
    address = models.TextField(blank=True, verbose_name="Campus Location / Address")
    description = models.TextField(blank=True, verbose_name="Hostel Facilities / Notes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Hostel Building"
        verbose_name_plural = "Hostel Buildings"

    def __str__(self):
        return f"{self.name} ({self.get_hostel_type_display()})"

    def clean(self):
        super().clean()
        if self.name:
            self.name = self.name.strip()


class HostelRoom(models.Model):
    """Individual room in a hostel"""
    ROOM_TYPE_CHOICES = [
        ('Single', 'Single Occupancy (1 Bed)'),
        ('Double', 'Double Sharing (2 Beds)'),
        ('Triple', 'Triple Sharing (3 Beds)'),
        ('Dormitory', 'Dormitory (4+ Beds)'),
    ]

    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='rooms', verbose_name="Hostel Building")
    room_number = models.CharField(max_length=30, verbose_name="Room Number")
    room_type = models.CharField(max_length=30, choices=ROOM_TYPE_CHOICES, default='Double', verbose_name="Room Type")
    capacity = models.PositiveIntegerField(default=2, verbose_name="Bed Capacity")
    monthly_rent = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('8000.00'), verbose_name="Monthly Rent (PKR)")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['hostel__name', 'room_number']
        unique_together = ('hostel', 'room_number')
        verbose_name = "Hostel Room"
        verbose_name_plural = "Hostel Rooms"

    def __str__(self):
        return f"{self.hostel.name} - Room {self.room_number}"

    @property
    def current_occupancy(self):
        return self.allocations.filter(status='Active').count()

    @property
    def is_full(self):
        return self.current_occupancy >= self.capacity

    @property
    def vacant_beds(self):
        return max(0, self.capacity - self.current_occupancy)


class RoomAllocation(models.Model):
    """Student hostel room occupancy record"""
    STATUS_CHOICES = [
        ('Active', 'Active Resident'),
        ('Vacated', 'Vacated / Checked-out'),
    ]

    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='hostel_allocations', verbose_name="Student")
    room = models.ForeignKey(HostelRoom, on_delete=models.CASCADE, related_name='allocations', verbose_name="Room")
    allocated_date = models.DateField(default=timezone.now, verbose_name="Check-in Date")
    vacated_date = models.DateField(null=True, blank=True, verbose_name="Check-out Date")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active', verbose_name="Resident Status")
    emergency_contact = models.CharField(max_length=100, blank=True, verbose_name="Emergency Guardian Contact")
    remarks = models.CharField(max_length=200, blank=True, verbose_name="Notes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-allocated_date', 'student__student_name']
        verbose_name = "Room Allocation"
        verbose_name_plural = "Room Allocations"

    def __str__(self):
        return f"{self.student.student_name} - {self.room}"

    def clean(self):
        super().clean()
        # Ensure room is not overbooked when creating or activating
        if self.status == 'Active' and self.room:
            current_active = self.room.allocations.filter(status='Active').exclude(pk=self.pk).count()
            if current_active >= self.room.capacity:
                raise ValidationError({'room': f"Room {self.room.room_number} is already at maximum capacity ({self.room.capacity} beds)."})
