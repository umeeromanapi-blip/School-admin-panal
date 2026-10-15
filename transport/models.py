from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal


class Vehicle(models.Model):
    """School bus or van vehicle record"""
    STATUS_CHOICES = [
        ('Active', 'Active in Service'),
        ('Maintenance', 'Under Maintenance'),
        ('Inactive', 'Decommissioned / Inactive'),
    ]

    vehicle_number = models.CharField(max_length=30, unique=True, verbose_name="Vehicle / Plate #")
    vehicle_model = models.CharField(max_length=100, verbose_name="Vehicle Model / Make")
    driver_name = models.CharField(max_length=120, verbose_name="Driver Full Name")
    driver_phone = models.CharField(max_length=25, verbose_name="Driver Contact Phone")
    driver_license = models.CharField(max_length=50, blank=True, verbose_name="Driver License #")
    seating_capacity = models.PositiveIntegerField(default=30, verbose_name="Seating Capacity")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active', verbose_name="Fleet Status")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['vehicle_number']
        verbose_name = "Fleet Vehicle"
        verbose_name_plural = "Fleet Vehicles"

    def __str__(self):
        return f"{self.vehicle_number} - {self.vehicle_model} ({self.driver_name})"

    def clean(self):
        super().clean()
        if self.vehicle_number:
            self.vehicle_number = self.vehicle_number.strip().upper()
        if self.driver_name:
            self.driver_name = self.driver_name.strip()
        if self.driver_phone:
            self.driver_phone = self.driver_phone.strip()


class Route(models.Model):
    """Bus transport route path and pricing"""
    route_name = models.CharField(max_length=150, unique=True, verbose_name="Route Name / Title")
    start_location = models.CharField(max_length=150, verbose_name="Origin / Start Point")
    end_location = models.CharField(max_length=150, verbose_name="Destination / Campus")
    monthly_fare = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('3500.00'), verbose_name="Monthly Fare (PKR)")
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True, related_name='routes', verbose_name="Assigned Bus / Van")
    description = models.TextField(blank=True, verbose_name="Route Stops & Itinerary")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['route_name']
        verbose_name = "Transport Route"
        verbose_name_plural = "Transport Routes"

    def __str__(self):
        return f"{self.route_name} ({self.start_location} -> {self.end_location})"

    def clean(self):
        super().clean()
        if self.route_name:
            self.route_name = self.route_name.strip()


class TransportAllocation(models.Model):
    """Assignment of a student to a daily transport route"""
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='transport_passes', verbose_name="Student")
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='assigned_students', verbose_name="Bus Route")
    pickup_stop = models.CharField(max_length=120, verbose_name="Designated Pickup Point")
    dropoff_stop = models.CharField(max_length=120, blank=True, verbose_name="Designated Drop-off Point")
    joined_date = models.DateField(default=timezone.now, verbose_name="Commencement Date")
    is_active = models.BooleanField(default=True, verbose_name="Active Transport Pass")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-joined_date', 'student__student_name']
        verbose_name = "Transport Allocation"
        verbose_name_plural = "Transport Allocations"

    def __str__(self):
        return f"{self.student.student_name} on {self.route.route_name}"

    def clean(self):
        super().clean()
        if self.pickup_stop:
            self.pickup_stop = self.pickup_stop.strip()
