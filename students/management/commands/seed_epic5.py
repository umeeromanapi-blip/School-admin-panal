import datetime
from decimal import Decimal
from django.core.management.base import BaseCommand
from students.models import Student
from transport.models import Vehicle, Route, TransportAllocation
from hostel.models import Hostel, HostelRoom, RoomAllocation


class Command(BaseCommand):
    help = 'Seeds sample data for Epic 5: Transport Fleet, Routes, Passes, Hostels, Rooms, and Resident Allocations'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE("Seeding Epic 5: Transport and Hostel Residential Services..."))

        # 1. Transport Fleet Vehicles
        vehicles_data = [
            {
                'vehicle_number': 'BUS-01',
                'vehicle_model': 'Toyota Coaster 2024 (30-Seater)',
                'driver_name': 'Muhammad Rafiq',
                'driver_phone': '0300-1234567',
                'driver_license': 'LTV-PK-88910',
                'seating_capacity': 30,
                'status': 'Active',
            },
            {
                'vehicle_number': 'BUS-02',
                'vehicle_model': 'Hino Rainbow Bus (45-Seater)',
                'driver_name': 'Tariq Mehmood',
                'driver_phone': '0312-9876543',
                'driver_license': 'HTV-PK-11029',
                'seating_capacity': 45,
                'status': 'Active',
            },
            {
                'vehicle_number': 'VAN-03',
                'vehicle_model': 'Toyota HiAce Grand Cabin (15-Seater)',
                'driver_name': 'Ghulam Mustafa',
                'driver_phone': '0333-5551234',
                'driver_license': 'LTV-PK-44321',
                'seating_capacity': 15,
                'status': 'Maintenance',
            },
        ]

        created_vehicles = []
        for vdata in vehicles_data:
            veh, _ = Vehicle.objects.update_or_create(
                vehicle_number=vdata['vehicle_number'],
                defaults=vdata
            )
            created_vehicles.append(veh)

        # 2. Bus Routes
        routes_data = [
            {
                'route_name': 'Route 1: Rawalpindi Saddar &ndash; I-8 &ndash; Campus',
                'start_location': 'Rawalpindi Saddar Station',
                'end_location': 'Main Campus Gate A',
                'monthly_fare': Decimal('4500.00'),
                'vehicle': created_vehicles[0],
                'description': 'Stops: 1. Saddar Metro, 2. Murree Road Chandni Chowk, 3. Faizabad Interchange, 4. I-8 Markaz, 5. School Campus.',
            },
            {
                'route_name': 'Route 2: Blue Area &ndash; F-8 &ndash; Campus',
                'start_location': 'Blue Area Metro Station',
                'end_location': 'Main Campus Gate B',
                'monthly_fare': Decimal('3800.00'),
                'vehicle': created_vehicles[1],
                'description': 'Stops: 1. Blue Area, 2. G-7 Markaz, 3. F-8/3 Roundabout, 4. G-9 Karachi Company, 5. School Campus.',
            },
            {
                'route_name': 'Route 3: Bahria Town &ndash; PWD &ndash; Expressway',
                'start_location': 'Bahria Town Phase 4',
                'end_location': 'Main Campus Gate A',
                'monthly_fare': Decimal('5500.00'),
                'vehicle': None,
                'description': 'Stops: 1. Civic Center Bahria, 2. PWD Main Gate, 3. Korang Bridge, 4. Islamabad Highway, 5. School Campus.',
            },
        ]

        created_routes = []
        for rdata in routes_data:
            route_obj, _ = Route.objects.update_or_create(
                route_name=rdata['route_name'],
                defaults=rdata
            )
            created_routes.append(route_obj)

        # 3. Student Transport Passes
        students = list(Student.objects.all())
        today = datetime.date.today()
        passes_created = 0

        if students and len(created_routes) >= 2:
            TransportAllocation.objects.update_or_create(
                student=students[0],
                defaults={
                    'route': created_routes[0],
                    'pickup_stop': 'Faizabad Metro Stop',
                    'dropoff_stop': 'Main Campus Gate A',
                    'joined_date': today - datetime.timedelta(days=60),
                    'is_active': True,
                }
            )
            passes_created += 1

            if len(students) > 1:
                TransportAllocation.objects.update_or_create(
                    student=students[1],
                    defaults={
                        'route': created_routes[0],
                        'pickup_stop': 'Chandni Chowk Stop',
                        'dropoff_stop': 'Main Campus Gate A',
                        'joined_date': today - datetime.timedelta(days=45),
                        'is_active': True,
                    }
                )
                passes_created += 1

            if len(students) > 2:
                TransportAllocation.objects.update_or_create(
                    student=students[2],
                    defaults={
                        'route': created_routes[1],
                        'pickup_stop': 'F-8/3 Roundabout',
                        'dropoff_stop': 'Main Campus Gate B',
                        'joined_date': today - datetime.timedelta(days=30),
                        'is_active': True,
                    }
                )
                passes_created += 1

        # 4. Hostels
        hostels_data = [
            {
                'name': 'Iqbal Hall (Senior Boys Residence)',
                'hostel_type': 'Boys',
                'warden_name': 'Ustadh Qasim Farooq',
                'warden_phone': '0300-8877665',
                'address': 'West Campus Residential Quad, Sector H-8',
                'description': 'Modern dormitories with 24/7 power backup, high-speed WiFi, laundry facilities, and dining mess.',
            },
            {
                'name': 'Fatima Hall (Girls Residence)',
                'hostel_type': 'Girls',
                'warden_name': 'Mrs. Bushra Perveen',
                'warden_phone': '0321-4433221',
                'address': 'East Campus Residential Complex, Sector H-8',
                'description': 'Secure enclosed residency with biometrics, dedicated warden quarters, reading library, and medical room.',
            },
        ]

        created_hostels = []
        for hdata in hostels_data:
            hostel_obj, _ = Hostel.objects.update_or_create(
                name=hdata['name'],
                defaults=hdata
            )
            created_hostels.append(hostel_obj)

        # 5. Hostel Rooms
        rooms_data = [
            # Iqbal Hall
            {'hostel': created_hostels[0], 'room_number': '101', 'room_type': 'Double', 'capacity': 2, 'monthly_rent': Decimal('9000.00')},
            {'hostel': created_hostels[0], 'room_number': '102', 'room_type': 'Double', 'capacity': 2, 'monthly_rent': Decimal('9000.00')},
            {'hostel': created_hostels[0], 'room_number': '103', 'room_type': 'Single', 'capacity': 1, 'monthly_rent': Decimal('14000.00')},
            {'hostel': created_hostels[0], 'room_number': '201', 'room_type': 'Dormitory', 'capacity': 4, 'monthly_rent': Decimal('6500.00')},
            # Fatima Hall
            {'hostel': created_hostels[1], 'room_number': 'F-01', 'room_type': 'Double', 'capacity': 2, 'monthly_rent': Decimal('9500.00')},
            {'hostel': created_hostels[1], 'room_number': 'F-02', 'room_type': 'Triple', 'capacity': 3, 'monthly_rent': Decimal('7500.00')},
        ]

        created_rooms = []
        for rmdata in rooms_data:
            room_obj, _ = HostelRoom.objects.update_or_create(
                hostel=rmdata['hostel'],
                room_number=rmdata['room_number'],
                defaults=rmdata
            )
            created_rooms.append(room_obj)

        # 6. Room Allocations
        allocs_created = 0
        if len(students) >= 4 and len(created_rooms) >= 3:
            RoomAllocation.objects.update_or_create(
                student=students[3],
                defaults={
                    'room': created_rooms[0],
                    'allocated_date': today - datetime.timedelta(days=90),
                    'status': 'Active',
                    'emergency_contact': 'Father: 0300-1122334',
                    'remarks': 'Bed # 1 alloted. Paid term security.',
                }
            )
            allocs_created += 1

            if len(students) >= 5:
                RoomAllocation.objects.update_or_create(
                    student=students[4],
                    defaults={
                        'room': created_rooms[0],
                        'allocated_date': today - datetime.timedelta(days=75),
                        'status': 'Active',
                        'emergency_contact': 'Guardian: 0321-9988776',
                        'remarks': 'Bed # 2 alloted.',
                    }
                )
                allocs_created += 1

            if len(students) >= 6:
                RoomAllocation.objects.update_or_create(
                    student=students[5],
                    defaults={
                        'room': created_rooms[2],
                        'allocated_date': today - datetime.timedelta(days=40),
                        'status': 'Active',
                        'emergency_contact': 'Uncle: 0345-5544332',
                        'remarks': 'Single room allocated for study focus.',
                    }
                )
                allocs_created += 1

        self.stdout.write(self.style.SUCCESS(
            f"Epic 5 seed complete: {len(created_vehicles)} vehicles, {len(created_routes)} routes, "
            f"{passes_created} transport passes, {len(created_hostels)} hostels, {len(created_rooms)} rooms, "
            f"and {allocs_created} student residential allocations."
        ))
