import datetime
from django.test import TestCase, Client
from django.urls import reverse
from students.models import Student
from teachers.models import Teacher
from fees.models import FeeRecord
from attendance.models import AttendanceRecord
from teachers.forms import TeacherForm
from fees.forms import FeeRecordForm
from attendance.forms import AttendanceDateForm


# ─────────────────────────────────────────────────────────────────────────────
# TEACHER TESTS
# ─────────────────────────────────────────────────────────────────────────────

class TeacherModelAndFormTests(TestCase):

    def test_teacher_str(self):
        t = Teacher.objects.create(
            employee_id='TCH-T01', full_name='Test Teacher', phone='03000000001',
            department='Science', subject='Chemistry',
            date_joined=datetime.date.today()
        )
        self.assertEqual(str(t), 'Test Teacher (TCH-T01)')

    def test_form_valid(self):
        form = TeacherForm(data={
            'employee_id': 'TCH-FORM1',
            'full_name': 'Valid Teacher',
            'phone': '03001111111',
            'email': 'valid@school.edu',
            'department': 'Mathematics',
            'subject': 'Algebra',
            'assigned_class': 'Class 9-A',
            'qualification': 'M.Sc Math',
            'date_joined': datetime.date.today().isoformat(),
            'status': 'Active',
        })
        self.assertTrue(form.is_valid(), form.errors)
        # Employee ID normalized to uppercase
        self.assertEqual(form.cleaned_data['employee_id'], 'TCH-FORM1')

    def test_form_missing_required_fields(self):
        form = TeacherForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('employee_id', form.errors)
        self.assertIn('full_name', form.errors)
        self.assertIn('phone', form.errors)
        self.assertIn('subject', form.errors)
        self.assertIn('date_joined', form.errors)

    def test_form_duplicate_employee_id(self):
        Teacher.objects.create(
            employee_id='TCH-DUP', full_name='Existing', phone='03009999991',
            department='English', subject='English', date_joined=datetime.date.today()
        )
        form = TeacherForm(data={
            'employee_id': 'tch-dup',  # case-insensitive duplicate
            'full_name': 'Another Teacher',
            'phone': '03009999992',
            'department': 'English',
            'subject': 'English',
            'date_joined': datetime.date.today().isoformat(),
            'status': 'Active',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('employee_id', form.errors)

    def test_form_invalid_phone(self):
        form = TeacherForm(data={
            'employee_id': 'TCH-PH1',
            'full_name': 'Phone Test',
            'phone': 'not-a-number',
            'department': 'Science',
            'subject': 'Biology',
            'date_joined': datetime.date.today().isoformat(),
            'status': 'Active',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('phone', form.errors)


class TeacherViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.teacher = Teacher.objects.create(
            employee_id='TCH-V01', full_name='View Teacher', phone='03001234568',
            department='Mathematics', subject='Calculus',
            date_joined=datetime.date.today(), status='Active'
        )

    def test_teacher_list_renders(self):
        r = self.client.get(reverse('teachers:teacher_list'))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'View Teacher')
        self.assertContains(r, 'TCH-V01')

    def test_teacher_list_search(self):
        r = self.client.get(reverse('teachers:teacher_list'), {'q': 'View Teacher'})
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'View Teacher')

    def test_teacher_add_get(self):
        r = self.client.get(reverse('teachers:teacher_add'))
        self.assertEqual(r.status_code, 200)
        self.assertIn('form', r.context)

    def test_teacher_add_post_valid(self):
        data = {
            'employee_id': 'TCH-NEW1',
            'full_name': 'Brand New Teacher',
            'phone': '03007777777',
            'email': '',
            'department': 'Urdu',
            'subject': 'Urdu Literature',
            'assigned_class': 'Class 8-A',
            'qualification': 'MA Urdu',
            'date_joined': datetime.date.today().isoformat(),
            'status': 'Active',
        }
        r = self.client.post(reverse('teachers:teacher_add'), data=data, follow=True)
        self.assertEqual(r.status_code, 200)
        self.assertTrue(Teacher.objects.filter(employee_id='TCH-NEW1').exists())
        self.assertContains(r, 'added successfully')

    def test_teacher_add_post_invalid_missing_fields(self):
        initial = Teacher.objects.count()
        r = self.client.post(reverse('teachers:teacher_add'), data={})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Teacher.objects.count(), initial)

    def test_teacher_edit(self):
        url = reverse('teachers:teacher_edit', args=[self.teacher.id])
        data = {
            'employee_id': 'TCH-V01',
            'full_name': 'Updated Teacher Name',
            'phone': '03001234568',
            'email': '',
            'department': 'Mathematics',
            'subject': 'Advanced Calculus',
            'assigned_class': '',
            'qualification': 'PhD Math',
            'date_joined': self.teacher.date_joined.isoformat(),
            'status': 'Active',
        }
        r = self.client.post(url, data=data, follow=True)
        self.assertEqual(r.status_code, 200)
        self.teacher.refresh_from_db()
        self.assertEqual(self.teacher.full_name, 'Updated Teacher Name')
        self.assertEqual(self.teacher.subject, 'Advanced Calculus')

    def test_teacher_delete_get_shows_confirm(self):
        r = self.client.get(reverse('teachers:teacher_delete', args=[self.teacher.id]))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'View Teacher')
        self.assertTrue(Teacher.objects.filter(id=self.teacher.id).exists())

    def test_teacher_delete_post_removes_record(self):
        r = self.client.post(reverse('teachers:teacher_delete', args=[self.teacher.id]), follow=True)
        self.assertEqual(r.status_code, 200)
        self.assertFalse(Teacher.objects.filter(id=self.teacher.id).exists())
        self.assertContains(r, 'removed successfully')

    def test_teacher_detail_view(self):
        r = self.client.get(reverse('teachers:teacher_detail', args=[self.teacher.id]))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'View Teacher')
        self.assertContains(r, 'TCH-V01')


# ─────────────────────────────────────────────────────────────────────────────
# FEE TESTS
# ─────────────────────────────────────────────────────────────────────────────

class FeeFormTests(TestCase):

    def setUp(self):
        self.student = Student.objects.create(
            student_name='Fee Student', admission_number='FEE-001',
            student_class='Class 9', contact_number='03000000002'
        )

    def test_fee_form_valid(self):
        form = FeeRecordForm(data={
            'student': self.student.id,
            'fee_type': 'Monthly Tuition',
            'amount_due': '2500.00',
            'amount_paid': '2500.00',
            'status': 'Paid',
            'month': 10,
            'year': 2026,
            'due_date': datetime.date.today().isoformat(),
            'payment_date': datetime.date.today().isoformat(),
            'remarks': '',
        })
        self.assertTrue(form.is_valid(), form.errors)

    def test_fee_form_paid_exceeds_due(self):
        form = FeeRecordForm(data={
            'student': self.student.id,
            'fee_type': 'Monthly Tuition',
            'amount_due': '1000.00',
            'amount_paid': '2000.00',  # exceeds due
            'status': 'Paid',
            'month': 10,
            'year': 2026,
            'due_date': datetime.date.today().isoformat(),
            'remarks': '',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)

    def test_fee_form_negative_amount(self):
        form = FeeRecordForm(data={
            'student': self.student.id,
            'fee_type': 'Exam Fee',
            'amount_due': '-500.00',
            'amount_paid': '0',
            'status': 'Unpaid',
            'month': 10,
            'year': 2026,
            'due_date': datetime.date.today().isoformat(),
            'remarks': '',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('amount_due', form.errors)


class FeeViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.student = Student.objects.create(
            student_name='Fee View Student', admission_number='FEE-VIEW-001',
            student_class='Class 10', contact_number='03000000003'
        )
        self.fee = FeeRecord.objects.create(
            student=self.student, fee_type='Monthly Tuition',
            amount_due=3000, amount_paid=3000,
            status='Paid', due_date=datetime.date.today()
        )

    def test_fee_list_renders(self):
        r = self.client.get(reverse('fees:fee_list'))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Fee View Student')

    def test_fee_add_get(self):
        r = self.client.get(reverse('fees:fee_add'))
        self.assertEqual(r.status_code, 200)
        self.assertIn('form', r.context)

    def test_fee_add_post_valid(self):
        data = {
            'student': self.student.id,
            'fee_type': 'Exam Fee',
            'amount_due': '1500',
            'amount_paid': '0',
            'status': 'Unpaid',
            'month': 10,
            'year': 2026,
            'due_date': datetime.date.today().isoformat(),
            'payment_date': '',
            'remarks': '',
        }
        r = self.client.post(reverse('fees:fee_add'), data=data, follow=True)
        self.assertEqual(r.status_code, 200)
        self.assertTrue(FeeRecord.objects.filter(fee_type='Exam Fee', student=self.student).exists())

    def test_fee_edit(self):
        url = reverse('fees:fee_edit', args=[self.fee.id])
        data = {
            'student': self.student.id,
            'fee_type': 'Monthly Tuition',
            'amount_due': '3000',
            'amount_paid': '3000',
            'status': 'Paid',
            'month': 10,
            'year': 2026,
            'due_date': datetime.date.today().isoformat(),
            'payment_date': '',
            'remarks': 'Updated',
        }
        r = self.client.post(url, data=data, follow=True)
        self.assertEqual(r.status_code, 200)
        self.fee.refresh_from_db()
        self.assertEqual(self.fee.remarks, 'Updated')

    def test_fee_delete_get_confirm(self):
        r = self.client.get(reverse('fees:fee_delete', args=[self.fee.id]))
        self.assertEqual(r.status_code, 200)
        self.assertTrue(FeeRecord.objects.filter(id=self.fee.id).exists())

    def test_fee_delete_post_removes(self):
        r = self.client.post(reverse('fees:fee_delete', args=[self.fee.id]), follow=True)
        self.assertEqual(r.status_code, 200)
        self.assertFalse(FeeRecord.objects.filter(id=self.fee.id).exists())


# ─────────────────────────────────────────────────────────────────────────────
# ATTENDANCE TESTS
# ─────────────────────────────────────────────────────────────────────────────

class AttendanceFormTests(TestCase):

    def test_future_date_rejected(self):
        form = AttendanceDateForm(
            data={
                'date': (datetime.date.today() + datetime.timedelta(days=1)).isoformat(),
                'student_class': 'Class 9-A',
            },
            class_choices=[('Class 9-A', 'Class 9-A')]
        )
        self.assertFalse(form.is_valid())
        self.assertIn('date', form.errors)

    def test_valid_past_date(self):
        form = AttendanceDateForm(
            data={
                'date': (datetime.date.today() - datetime.timedelta(days=1)).isoformat(),
                'student_class': 'Class 9-A',
            },
            class_choices=[('Class 9-A', 'Class 9-A')]
        )
        self.assertTrue(form.is_valid(), form.errors)


class AttendanceViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.student = Student.objects.create(
            student_name='Att Student', admission_number='ATT-001',
            student_class='Class 8-A', contact_number='03000000004'
        )
        self.record = AttendanceRecord.objects.create(
            student=self.student,
            date=datetime.date.today() - datetime.timedelta(days=1),
            status='Present', marked_by='Test Admin'
        )

    def test_attendance_list_renders(self):
        r = self.client.get(reverse('attendance:attendance_list'))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Att Student')

    def test_attendance_list_date_filter(self):
        r = self.client.get(reverse('attendance:attendance_list'), {'date': self.record.date.isoformat()})
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Att Student')

    def test_attendance_mark_get(self):
        r = self.client.get(reverse('attendance:attendance_mark'))
        self.assertEqual(r.status_code, 200)
        self.assertIn('selector_form', r.context)

    def test_attendance_mark_load_class(self):
        r = self.client.post(reverse('attendance:attendance_mark'), data={
            'date': datetime.date.today().isoformat(),
            'student_class': 'Class 8-A',
        })
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Att Student')

    def test_attendance_mark_save(self):
        post_data = {
            'att_date': datetime.date.today().isoformat(),
            'mark_attendance': '1',
            'student_ids': [str(self.student.id)],
            f'status_{self.student.id}': 'Present',
            f'remarks_{self.student.id}': 'On time',
            'marked_by': 'Test Teacher',
        }
        r = self.client.post(reverse('attendance:attendance_mark'), data=post_data, follow=True)
        self.assertEqual(r.status_code, 200)
        self.assertTrue(AttendanceRecord.objects.filter(
            student=self.student,
            date=datetime.date.today(),
            status='Present'
        ).exists())
        self.assertContains(r, 'Attendance marked')

    def test_attendance_unique_per_student_per_day(self):
        """Cannot have two attendance records for same student on same day."""
        with self.assertRaises(Exception):
            AttendanceRecord.objects.create(
                student=self.student,
                date=self.record.date,
                status='Absent'
            )

    def test_attendance_edit(self):
        url = reverse('attendance:attendance_edit', args=[self.record.id])
        data = {
            'student': self.student.id,
            'date': self.record.date.isoformat(),
            'status': 'Late',
            'remarks': 'Arrived 10 minutes late',
            'marked_by': 'Updated Admin',
        }
        r = self.client.post(url, data=data, follow=True)
        self.assertEqual(r.status_code, 200)
        self.record.refresh_from_db()
        self.assertEqual(self.record.status, 'Late')

    def test_attendance_delete_get_confirm(self):
        r = self.client.get(reverse('attendance:attendance_delete', args=[self.record.id]))
        self.assertEqual(r.status_code, 200)
        self.assertTrue(AttendanceRecord.objects.filter(id=self.record.id).exists())

    def test_attendance_delete_post_removes(self):
        r = self.client.post(reverse('attendance:attendance_delete', args=[self.record.id]), follow=True)
        self.assertEqual(r.status_code, 200)
        self.assertFalse(AttendanceRecord.objects.filter(id=self.record.id).exists())

    def test_student_attendance_report(self):
        url = reverse('attendance:attendance_student_report', args=[self.student.id])
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Att Student')
        self.assertContains(r, 'Attendance Rate')


# ─────────────────────────────────────────────────────────────────────────────
# REPORTS VIEW TESTS
# ─────────────────────────────────────────────────────────────────────────────

class ReportsViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        # Minimal data so the reports page can render counts
        Student.objects.create(
            student_name='Report Student', admission_number='RPT-001',
            student_class='Class 10', contact_number='03000000005'
        )
        Teacher.objects.create(
            employee_id='RPT-TCH-01', full_name='Report Teacher',
            phone='03000000006', department='Science',
            subject='Biology', date_joined=datetime.date.today()
        )

    def test_reports_overview_renders(self):
        r = self.client.get('/reports/')
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Reports')
        self.assertContains(r, 'Total Students')
        self.assertContains(r, 'Total Teachers')
        self.assertContains(r, 'Fee Collection')
        self.assertContains(r, 'Attendance Rate')

    def test_reports_has_correct_counts(self):
        r = self.client.get('/reports/')
        self.assertEqual(r.context['total_students'], 1)
        self.assertEqual(r.context['total_teachers'], 1)
