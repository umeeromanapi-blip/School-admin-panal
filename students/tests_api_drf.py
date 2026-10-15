import json
from django.test import TestCase, Client
from django.urls import reverse
from students.models import Student
from teachers.models import Teacher
from attendance.models import AttendanceRecord
from fees.models import FeeRecord
from announcements.models import Announcement
from exams.models import Subject, Exam, Mark


class RestApiComprehensiveTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.student = Student.objects.create(
            student_name="Zayd Ali",
            admission_number="ADM-101",
            student_class="Class 8",
            contact_number="03001112233"
        )
        self.teacher = Teacher.objects.create(
            employee_id="TCH-001",
            full_name="Prof. Ahmed Khan",
            phone="03009998877",
            department="Science",
            subject="Physics",
            date_joined="2023-01-15",
            status="Active"
        )

    def test_api_root(self):
        """GET /api/ returns API directory listing."""
        response = self.client.get('/api/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('endpoints', data)
        self.assertIn('students', data['endpoints'])

    def test_student_list_and_search(self):
        """GET /api/students/ returns list and filters by q and class."""
        response = self.client.get('/api/students/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['student_name'], "Zayd Ali")

        # Test search query
        resp_q = self.client.get('/api/students/?q=Zayd')
        self.assertEqual(len(json.loads(resp_q.content)), 1)

        resp_q_none = self.client.get('/api/students/?q=NonExistent')
        self.assertEqual(len(json.loads(resp_q_none.content)), 0)

    def test_student_create_post(self):
        """POST /api/students/ creates student record via DRF."""
        payload = {
            'student_name': 'Sara Fatima',
            'admission_number': 'ADM-102',
            'student_class': 'Class 9',
            'contact_number': '03002223344'
        }
        response = self.client.post(
            '/api/students/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.content)
        self.assertEqual(data['admission_number'], 'ADM-102')
        self.assertTrue(Student.objects.filter(admission_number='ADM-102').exists())

    def test_student_create_invalid_and_duplicate(self):
        """POST invalid returns 400 Bad Request with field errors."""
        # Duplicate admission number
        payload = {
            'student_name': 'Duplicate Person',
            'admission_number': 'ADM-101',
            'student_class': 'Class 8',
            'contact_number': '03003334455'
        }
        response = self.client.post(
            '/api/students/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn('admission_number', data['errors'])

    def test_student_detail_get_put_patch_delete(self):
        """Full CRUD on /api/students/<id>/."""
        url = f'/api/students/{self.student.id}/'

        # GET detail
        resp_get = self.client.get(url)
        self.assertEqual(resp_get.status_code, 200)
        self.assertEqual(json.loads(resp_get.content)['id'], self.student.id)

        # PATCH partial update
        patch_payload = {'contact_number': '03998887766'}
        resp_patch = self.client.patch(url, data=json.dumps(patch_payload), content_type='application/json')
        self.assertEqual(resp_patch.status_code, 200)
        self.student.refresh_from_db()
        self.assertEqual(self.student.contact_number, '03998887766')

        # PUT full update
        put_payload = {
            'student_name': 'Zayd Ali Khan',
            'admission_number': 'ADM-101',
            'student_class': 'Class 8-A',
            'contact_number': '03998887766'
        }
        resp_put = self.client.put(url, data=json.dumps(put_payload), content_type='application/json')
        self.assertEqual(resp_put.status_code, 200)
        self.student.refresh_from_db()
        self.assertEqual(self.student.student_name, 'Zayd Ali Khan')

        # DELETE
        resp_del = self.client.delete(url)
        self.assertEqual(resp_del.status_code, 204)
        self.assertFalse(Student.objects.filter(id=self.student.id).exists())

    def test_dashboard_stats_api(self):
        """GET /api/dashboard/stats/ returns aggregated school metrics."""
        response = self.client.get('/api/dashboard/stats/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['total_students'], 1)
        self.assertIn('class_stats', data)

    def test_teachers_api(self):
        """Test GET and POST on /api/teachers/."""
        resp_list = self.client.get('/api/teachers/')
        self.assertEqual(resp_list.status_code, 200)
        data = json.loads(resp_list.content)
        self.assertEqual(len(data), 1)

        new_tch = {
            'employee_id': 'TCH-002',
            'full_name': 'Mrs. Nadia Bilal',
            'phone': '03112223344',
            'department': 'Mathematics',
            'subject': 'Algebra',
            'date_joined': '2023-09-01',
            'status': 'Active'
        }
        resp_post = self.client.post('/api/teachers/', data=json.dumps(new_tch), content_type='application/json')
        self.assertEqual(resp_post.status_code, 201)

    def test_attendance_api(self):
        """Test GET and POST on /api/attendance/."""
        payload = {
            'student': self.student.id,
            'date': '2026-10-15',
            'status': 'Present',
            'marked_by': 'Admin'
        }
        resp_post = self.client.post('/api/attendance/', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(resp_post.status_code, 201)

        resp_list = self.client.get('/api/attendance/')
        self.assertEqual(resp_list.status_code, 200)
        data = json.loads(resp_list.content)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['student_name'], 'Zayd Ali')

    def test_fees_api(self):
        """Test GET and POST on /api/fees/."""
        payload = {
            'student': self.student.id,
            'fee_type': 'Monthly Tuition',
            'amount_due': '5000.00',
            'amount_paid': '5000.00',
            'status': 'Paid',
            'due_date': '2026-10-10'
        }
        resp_post = self.client.post('/api/fees/', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(resp_post.status_code, 201)

        resp_list = self.client.get('/api/fees/')
        self.assertEqual(resp_list.status_code, 200)
        data = json.loads(resp_list.content)
        self.assertEqual(len(data), 1)

    def test_announcements_api(self):
        """Test GET and POST on /api/announcements/."""
        payload = {
            'title': 'School Sports Day',
            'category': 'sports',
            'content': 'Annual sports gala next Friday.',
            'audience': 'all',
            'priority': 'high',
            'is_pinned': True,
            'is_active': True,
            'published_date': '2026-10-15'
        }
        resp_post = self.client.post('/api/announcements/', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(resp_post.status_code, 201)

        resp_list = self.client.get('/api/announcements/')
        self.assertEqual(resp_list.status_code, 200)
        data = json.loads(resp_list.content)
        self.assertEqual(len(data), 1)
