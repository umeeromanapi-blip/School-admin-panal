import datetime
from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.utils import timezone
from students.models import Student
from transport.models import Vehicle, Route, TransportAllocation
from hostel.models import Hostel, HostelRoom, RoomAllocation


class VehicleModelAndViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.vehicle = Vehicle.objects.create(
            vehicle_number="BUS-01",
            vehicle_model="Toyota Coaster 2024",
            driver_name="Muhammad Rafiq",
            driver_phone="03001234567",
            driver_license="LTV-112233",
            seating_capacity=30,
            status="Active"
        )

    def test_vehicle_str_and_normalization(self):
        v = Vehicle(
            vehicle_number="bus-99",
            vehicle_model="HiAce",
            driver_name="Ali",
            driver_phone="0300123"
        )
        v.clean()
        self.assertEqual(v.vehicle_number, "BUS-99")
        self.assertIn("BUS-01", str(self.vehicle))
        self.assertIn("Rafiq", str(self.vehicle))

    def test_vehicle_list_view(self):
        res = self.client.get(reverse('transport:vehicle_list'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "BUS-01")
        self.assertContains(res, "Toyota Coaster")

    def test_vehicle_create_view(self):
        res = self.client.post(reverse('transport:vehicle_add'), {
            'vehicle_number': 'VAN-09',
            'vehicle_model': 'Toyota HiAce 2023',
            'driver_name': 'Tariq Mehmood',
            'driver_phone': '03119876543',
            'driver_license': 'LTV-998877',
            'seating_capacity': 15,
            'status': 'Active'
        })
        self.assertEqual(res.status_code, 302)
        self.assertTrue(Vehicle.objects.filter(vehicle_number='VAN-09').exists())

    def test_vehicle_edit_view(self):
        res = self.client.post(reverse('transport:vehicle_edit', kwargs={'pk': self.vehicle.pk}), {
            'vehicle_number': 'BUS-01',
            'vehicle_model': 'Toyota Coaster Premium 2025',
            'driver_name': 'Muhammad Rafiq Khan',
            'driver_phone': '03001234567',
            'driver_license': 'LTV-112233',
            'seating_capacity': 32,
            'status': 'Maintenance'
        })
        self.assertEqual(res.status_code, 302)
        self.vehicle.refresh_from_db()
        self.assertEqual(self.vehicle.vehicle_model, 'Toyota Coaster Premium 2025')
        self.assertEqual(self.vehicle.status, 'Maintenance')

    def test_vehicle_delete_view(self):
        res = self.client.post(reverse('transport:vehicle_delete', kwargs={'pk': self.vehicle.pk}))
        self.assertEqual(res.status_code, 302)
        self.assertFalse(Vehicle.objects.filter(pk=self.vehicle.pk).exists())


class RouteModelAndViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.vehicle = Vehicle.objects.create(
            vehicle_number="BUS-02",
            vehicle_model="Hino Bus",
            driver_name="Akram Masih",
            driver_phone="03223344556",
            seating_capacity=45,
            status="Active"
        )
        self.route = Route.objects.create(
            route_name="Route Alpha (Blue Area)",
            start_location="Saddar Rawalpindi",
            end_location="Main Campus Gate",
            monthly_fare=Decimal('4200.00'),
            vehicle=self.vehicle,
            description="Via Peshawar Road and Kashmir Highway"
        )

    def test_route_str_and_properties(self):
        self.assertIn("Route Alpha", str(self.route))
        self.assertIn("Saddar Rawalpindi", str(self.route))

    def test_transport_dashboard_view(self):
        res = self.client.get(reverse('transport:transport_dashboard'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Route Alpha (Blue Area)")
        self.assertContains(res, "BUS-02")

    def test_route_create_view(self):
        res = self.client.post(reverse('transport:route_add'), {
            'route_name': 'Route Beta (Islamabad Expressway)',
            'start_location': 'Koral Chowk',
            'end_location': 'Main Campus Gate',
            'monthly_fare': '3800.00',
            'vehicle': self.vehicle.pk,
            'description': 'Direct express stop via Faizabad'
        })
        self.assertEqual(res.status_code, 302)
        self.assertTrue(Route.objects.filter(route_name__contains='Route Beta').exists())

    def test_route_edit_view(self):
        res = self.client.post(reverse('transport:route_edit', kwargs={'pk': self.route.pk}), {
            'route_name': 'Route Alpha (Executive Express)',
            'start_location': 'Saddar Rawalpindi',
            'end_location': 'Main Campus Gate',
            'monthly_fare': '4500.00',
            'vehicle': self.vehicle.pk,
            'description': 'Upgraded AC coach service'
        })
        self.assertEqual(res.status_code, 302)
        self.route.refresh_from_db()
        self.assertEqual(self.route.monthly_fare, Decimal('4500.00'))

    def test_route_delete_view(self):
        res = self.client.post(reverse('transport:route_delete', kwargs={'pk': self.route.pk}))
        self.assertEqual(res.status_code, 302)
        self.assertFalse(Route.objects.filter(pk=self.route.pk).exists())


class TransportAllocationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.student = Student.objects.create(
            admission_number="ADM-901",
            student_name="Hamza Abbasi",
            student_class="Class 9",
            contact_number="03001112223"
        )
        self.route = Route.objects.create(
            route_name="Route Express",
            start_location="G-9 Markaz",
            end_location="Main Campus Gate",
            monthly_fare=Decimal('3000.00')
        )
        self.allocation = TransportAllocation.objects.create(
            student=self.student,
            route=self.route,
            pickup_stop="G-9/2 Roundabout",
            dropoff_stop="Campus Gate 1",
            joined_date=timezone.now().date(),
            is_active=True
        )

    def test_allocation_str_and_list(self):
        self.assertIn("Hamza Abbasi", str(self.allocation))
        res = self.client.get(reverse('transport:allocation_list'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Hamza Abbasi")
        self.assertContains(res, "G-9/2 Roundabout")

    def test_allocation_create_view(self):
        student2 = Student.objects.create(
            admission_number="ADM-902",
            student_name="Sara Khan",
            student_class="Class 8",
            contact_number="03112223334"
        )
        res = self.client.post(reverse('transport:allocation_add'), {
            'student': student2.pk,
            'route': self.route.pk,
            'pickup_stop': 'F-10 Markaz',
            'dropoff_stop': 'Campus Gate 1',
            'joined_date': timezone.now().date().strftime('%Y-%m-%d'),
            'is_active': True
        })
        self.assertEqual(res.status_code, 302)
        self.assertTrue(TransportAllocation.objects.filter(student=student2).exists())

    def test_allocation_edit_and_delete(self):
        edit_res = self.client.post(reverse('transport:allocation_edit', kwargs={'pk': self.allocation.pk}), {
            'student': self.student.pk,
            'route': self.route.pk,
            'pickup_stop': 'G-9/1 Stop 4',
            'dropoff_stop': 'Campus Gate 2',
            'joined_date': self.allocation.joined_date.strftime('%Y-%m-%d'),
            'is_active': False
        })
        self.assertEqual(edit_res.status_code, 302)
        self.allocation.refresh_from_db()
        self.assertEqual(self.allocation.pickup_stop, 'G-9/1 Stop 4')
        self.assertFalse(self.allocation.is_active)

        del_res = self.client.post(reverse('transport:allocation_delete', kwargs={'pk': self.allocation.pk}))
        self.assertEqual(del_res.status_code, 302)
        self.assertFalse(TransportAllocation.objects.filter(pk=self.allocation.pk).exists())


class HostelModelAndViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.hostel = Hostel.objects.create(
            name="Iqbal Hall (Boys Residence)",
            hostel_type="Boys",
            warden_name="Ustadh Khalid Mehmood",
            warden_phone="03009988771",
            address="Sector H-8 Campus, West Wing",
            description="Modern furnished dorms with 24/7 power backup"
        )

    def test_hostel_str_and_overview(self):
        self.assertIn("Iqbal Hall", str(self.hostel))
        res = self.client.get(reverse('hostel:hostel_overview'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Iqbal Hall")
        self.assertContains(res, "Ustadh Khalid Mehmood")

    def test_hostel_create_view(self):
        res = self.client.post(reverse('hostel:hostel_add'), {
            'name': 'Fatima Hall (Girls Residence)',
            'hostel_type': 'Girls',
            'warden_name': 'Madam Shaista Parveen',
            'warden_phone': '03215556677',
            'address': 'Sector H-8 Campus, East Wing',
            'description': 'Secure gated female residence with study lounges'
        })
        self.assertEqual(res.status_code, 302)
        self.assertTrue(Hostel.objects.filter(name__contains='Fatima Hall').exists())

    def test_hostel_edit_and_delete(self):
        edit_res = self.client.post(reverse('hostel:hostel_edit', kwargs={'pk': self.hostel.pk}), {
            'name': 'Allama Iqbal Hall (Boys Residence)',
            'hostel_type': 'Boys',
            'warden_name': 'Ustadh Khalid Mehmood Alvi',
            'warden_phone': '03009988771',
            'address': 'Sector H-8 Campus, West Wing',
            'description': 'Updated facilities'
        })
        self.assertEqual(edit_res.status_code, 302)
        self.hostel.refresh_from_db()
        self.assertEqual(self.hostel.name, 'Allama Iqbal Hall (Boys Residence)')

        del_res = self.client.post(reverse('hostel:hostel_delete', kwargs={'pk': self.hostel.pk}))
        self.assertEqual(del_res.status_code, 302)
        self.assertFalse(Hostel.objects.filter(pk=self.hostel.pk).exists())


class HostelRoomAndAllocationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.hostel = Hostel.objects.create(
            name="Jinnah Hall",
            hostel_type="Boys",
            warden_name="Saeed Anwar",
            warden_phone="03335557788"
        )
        self.room = HostelRoom.objects.create(
            hostel=self.hostel,
            room_number="101",
            room_type="Single",
            capacity=1,
            monthly_rent=Decimal('10000.00')
        )
        self.student1 = Student.objects.create(
            admission_number="ADM-801",
            student_name="Zayd Ali",
            student_class="Class 10",
            contact_number="03007788990"
        )
        self.student2 = Student.objects.create(
            admission_number="ADM-802",
            student_name="Bilal Farooq",
            student_class="Class 10",
            contact_number="03008899001"
        )

    def test_room_str_and_properties(self):
        self.assertIn("101", str(self.room))
        self.assertEqual(self.room.current_occupancy, 0)
        self.assertEqual(self.room.vacant_beds, 1)
        self.assertFalse(self.room.is_full)

    def test_room_views(self):
        res = self.client.get(reverse('hostel:room_list'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "101")

        # Create new room
        post_res = self.client.post(reverse('hostel:room_add'), {
            'hostel': self.hostel.pk,
            'room_number': '102',
            'room_type': 'Double',
            'capacity': 2,
            'monthly_rent': '7500.00'
        })
        self.assertEqual(post_res.status_code, 302)
        self.assertTrue(HostelRoom.objects.filter(room_number='102').exists())

        # Edit room
        r102 = HostelRoom.objects.get(room_number='102')
        edit_res = self.client.post(reverse('hostel:room_edit', kwargs={'pk': r102.pk}), {
            'hostel': self.hostel.pk,
            'room_number': '102',
            'room_type': 'Double',
            'capacity': 2,
            'monthly_rent': '8000.00'
        })
        self.assertEqual(edit_res.status_code, 302)
        r102.refresh_from_db()
        self.assertEqual(r102.monthly_rent, Decimal('8000.00'))

        # Delete room
        del_res = self.client.post(reverse('hostel:room_delete', kwargs={'pk': r102.pk}))
        self.assertEqual(del_res.status_code, 302)
        self.assertFalse(HostelRoom.objects.filter(room_number='102').exists())

    def test_room_allocation_and_capacity_constraint(self):
        # 1. Allocate student1 to single room 101
        RoomAllocation.objects.create(
            student=self.student1,
            room=self.room,
            allocated_date=timezone.now().date(),
            status="Active"
        )
        self.room.refresh_from_db()
        self.assertEqual(self.room.current_occupancy, 1)
        self.assertEqual(self.room.vacant_beds, 0)
        self.assertTrue(self.room.is_full)

        # 2. Attempting to allocate student2 to same full room should raise ValidationError
        alloc2 = RoomAllocation(
            student=self.student2,
            room=self.room,
            allocated_date=timezone.now().date(),
            status="Active"
        )
        with self.assertRaises(ValidationError):
            alloc2.clean()

    def test_room_allocation_views(self):
        # List view
        res = self.client.get(reverse('hostel:allocation_list'))
        self.assertEqual(res.status_code, 200)

        # Create allocation via view
        post_res = self.client.post(reverse('hostel:allocation_add'), {
            'student': self.student1.pk,
            'room': self.room.pk,
            'allocated_date': timezone.now().date().strftime('%Y-%m-%d'),
            'status': 'Active',
            'emergency_contact': '03001234567',
            'remarks': 'Bed 1 near window'
        })
        self.assertEqual(post_res.status_code, 302)
        self.assertTrue(RoomAllocation.objects.filter(student=self.student1, status='Active').exists())

        alloc = RoomAllocation.objects.get(student=self.student1)
        self.assertEqual(alloc.remarks, 'Bed 1 near window')

        # Edit allocation / vacate
        edit_res = self.client.post(reverse('hostel:allocation_edit', kwargs={'pk': alloc.pk}), {
            'student': self.student1.pk,
            'room': self.room.pk,
            'allocated_date': alloc.allocated_date.strftime('%Y-%m-%d'),
            'status': 'Vacated',
            'emergency_contact': '03001234567',
            'remarks': 'Vacated upon semester end'
        })
        self.assertEqual(edit_res.status_code, 302)
        alloc.refresh_from_db()
        self.assertEqual(alloc.status, 'Vacated')

        # Delete allocation
        del_res = self.client.post(reverse('hostel:allocation_delete', kwargs={'pk': alloc.pk}))
        self.assertEqual(del_res.status_code, 302)
        self.assertFalse(RoomAllocation.objects.filter(pk=alloc.pk).exists())


class MainDashboardEpic5IntegrationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.vehicle = Vehicle.objects.create(
            vehicle_number="METRO-01",
            vehicle_model="Iveco Coach",
            driver_name="Zubair",
            driver_phone="03451122334"
        )
        self.route = Route.objects.create(
            route_name="Route Express",
            start_location="Saddar",
            end_location="Campus"
        )
        self.hostel = Hostel.objects.create(
            name="Alpha Dorm",
            hostel_type="Boys",
            warden_name="Mr. Ali",
            warden_phone="03001122334"
        )
        self.room = HostelRoom.objects.create(
            hostel=self.hostel,
            room_number="R-01",
            capacity=2
        )
        self.student = Student.objects.create(
            admission_number="ADM-777",
            student_name="Usman Tariq",
            student_class="Class 9",
            contact_number="03000000000"
        )
        self.alloc = RoomAllocation.objects.create(
            student=self.student,
            room=self.room,
            status="Active"
        )

    def test_dashboard_displays_epic5_metrics_and_navigation(self):
        res = self.client.get(reverse('students:dashboard'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Transport Fleet")
        self.assertContains(res, "Hostel Residency")
        self.assertContains(res, "Epic 5")
