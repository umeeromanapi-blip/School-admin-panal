from django import forms
from .models import Vehicle, Route, TransportAllocation
from students.models import Student


class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ['vehicle_number', 'vehicle_model', 'driver_name', 'driver_phone', 'driver_license', 'seating_capacity', 'status']
        widgets = {
            'vehicle_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. BUS-01 / ICT-9821', 'id': 'id_vehicle_number'}),
            'vehicle_model': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Toyota Coaster 2024', 'id': 'id_vehicle_model'}),
            'driver_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Muhammad Rafiq', 'id': 'id_driver_name'}),
            'driver_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 03001234567', 'id': 'id_driver_phone'}),
            'driver_license': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. LTV-882910', 'id': 'id_driver_license'}),
            'seating_capacity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'id': 'id_seating_capacity'}),
            'status': forms.Select(attrs={'class': 'form-control', 'id': 'id_status'}),
        }


class RouteForm(forms.ModelForm):
    class Meta:
        model = Route
        fields = ['route_name', 'start_location', 'end_location', 'monthly_fare', 'vehicle', 'description']
        widgets = {
            'route_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Blue Area - F-8 Express', 'id': 'id_route_name'}),
            'start_location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Rawalpindi Saddar', 'id': 'id_start_location'}),
            'end_location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Main Campus Gate', 'id': 'id_end_location'}),
            'monthly_fare': forms.NumberInput(attrs={'class': 'form-control', 'step': '100.00', 'min': '0', 'id': 'id_monthly_fare'}),
            'vehicle': forms.Select(attrs={'class': 'form-control', 'id': 'id_vehicle'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'List key stops e.g. Stop 1: Metro, Stop 2: G-9 Markaz...', 'id': 'id_description'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['vehicle'].queryset = Vehicle.objects.filter(status='Active').order_by('vehicle_number')
        self.fields['vehicle'].required = False
        self.fields['vehicle'].empty_label = "-- Select Assigned Bus (Optional) --"


class TransportAllocationForm(forms.ModelForm):
    class Meta:
        model = TransportAllocation
        fields = ['student', 'route', 'pickup_stop', 'dropoff_stop', 'joined_date', 'is_active']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-control', 'id': 'id_student'}),
            'route': forms.Select(attrs={'class': 'form-control', 'id': 'id_route'}),
            'pickup_stop': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Peshawar Morr Stop', 'id': 'id_pickup_stop'}),
            'dropoff_stop': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. School Campus Gate', 'id': 'id_dropoff_stop'}),
            'joined_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'id': 'id_joined_date'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'id_is_active'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['student'].queryset = Student.objects.all().order_by('student_name')
        self.fields['student'].label_from_instance = lambda s: f"{s.student_name} ({s.student_class} - {s.admission_number})"
        self.fields['route'].queryset = Route.objects.all().order_by('route_name')
