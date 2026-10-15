from django import forms
from django.core.exceptions import ValidationError
from .models import Hostel, HostelRoom, RoomAllocation
from students.models import Student


class HostelForm(forms.ModelForm):
    class Meta:
        model = Hostel
        fields = ['name', 'hostel_type', 'warden_name', 'warden_phone', 'address', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Iqbal Hall (Boys Residence)', 'id': 'id_name'}),
            'hostel_type': forms.Select(attrs={'class': 'form-control', 'id': 'id_hostel_type'}),
            'warden_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Ustadh Khalid Mehmood', 'id': 'id_warden_name'}),
            'warden_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 03009988771', 'id': 'id_warden_phone'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Sector H-8 Campus, West Wing', 'id': 'id_address'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Mess facilities, curfew rules, wifi etc.', 'id': 'id_description'}),
        }


class HostelRoomForm(forms.ModelForm):
    class Meta:
        model = HostelRoom
        fields = ['hostel', 'room_number', 'room_type', 'capacity', 'monthly_rent']
        widgets = {
            'hostel': forms.Select(attrs={'class': 'form-control', 'id': 'id_hostel'}),
            'room_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 101, 204-A', 'id': 'id_room_number'}),
            'room_type': forms.Select(attrs={'class': 'form-control', 'id': 'id_room_type'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '20', 'id': 'id_capacity'}),
            'monthly_rent': forms.NumberInput(attrs={'class': 'form-control', 'step': '500.00', 'min': '0', 'id': 'id_monthly_rent'}),
        }


class RoomAllocationForm(forms.ModelForm):
    class Meta:
        model = RoomAllocation
        fields = ['student', 'room', 'allocated_date', 'status', 'emergency_contact', 'remarks']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-control', 'id': 'id_student'}),
            'room': forms.Select(attrs={'class': 'form-control', 'id': 'id_room'}),
            'allocated_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'id': 'id_allocated_date'}),
            'status': forms.Select(attrs={'class': 'form-control', 'id': 'id_status'}),
            'emergency_contact': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Guardian phone e.g. 03001234567', 'id': 'id_emergency_contact'}),
            'remarks': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Allotted bed number, luggage notes...', 'id': 'id_remarks'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['student'].queryset = Student.objects.all().order_by('student_name')
        self.fields['student'].label_from_instance = lambda s: f"{s.student_name} ({s.student_class} - {s.admission_number})"
        self.fields['room'].queryset = HostelRoom.objects.select_related('hostel').all().order_by('hostel__name', 'room_number')
        self.fields['room'].label_from_instance = lambda r: f"{r.hostel.name} - Room {r.room_number} ({r.vacant_beds} beds free)"
