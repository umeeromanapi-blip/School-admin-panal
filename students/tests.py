import json
from django.test import TestCase, Client
from django.urls import reverse
from .models import Student
from .forms import StudentForm


class StudentModelAndFormTests(TestCase):
    """
    Unit tests for Student model constraints and StudentForm validation rules.
    """

    def test_student_str_representation(self):
        student = Student.objects.create(
            student_name="Ali Khan",
            admission_number="ADM-001",
            student_class="Class 8",
            contact_number="03001234567"
        )
        self.assertEqual(str(student), "Ali Khan (ADM-001)")

    def test_contact_number_preserves_leading_zeros(self):
        """TC-04 verification: contact numbers must preserve leading zeros as text."""
        student = Student.objects.create(
            student_name="Sara Ahmed",
            admission_number="ADM-002",
            student_class="Class 9",
            contact_number="03009876543"
        )
        fetched = Student.objects.get(id=student.id)
        self.assertEqual(fetched.contact_number, "03009876543")
        self.assertTrue(fetched.contact_number.startswith("0"))

    def test_form_valid_data(self):
        """TC-01: Form accepts valid data."""
        form = StudentForm(data={
            'student_name': 'Zayd Hassan',
            'admission_number': 'adm-100',
            'student_class': 'Grade 10',
            'contact_number': '+923001234567',
        })
        self.assertTrue(form.is_valid(), form.errors)
        # Check that admission number gets normalized to uppercase
        self.assertEqual(form.cleaned_data['admission_number'], 'ADM-100')

    def test_form_missing_required_fields(self):
        """TC-02: Missing fields are rejected."""
        form = StudentForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('student_name', form.errors)
        self.assertIn('admission_number', form.errors)
        self.assertIn('student_class', form.errors)
        self.assertIn('contact_number', form.errors)

    def test_form_whitespace_only_rejected(self):
        """Whitespace only strings are rejected as empty."""
        form = StudentForm(data={
            'student_name': '   ',
            'admission_number': '   ',
            'student_class': '   ',
            'contact_number': '   ',
        })
        self.assertFalse(form.is_valid())

    def test_form_duplicate_admission_number_rejected(self):
        """TC-03: Duplicate admission number is rejected with informative error."""
        Student.objects.create(
            student_name="Original Student",
            admission_number="ADM-DUP",
            student_class="Class 7",
            contact_number="03211111111"
        )
        form = StudentForm(data={
            'student_name': 'Copycat Student',
            'admission_number': 'adm-dup',  # Case insensitive duplicate
            'student_class': 'Class 8',
            'contact_number': '03222222222',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('admission_number', form.errors)
        self.assertIn('already exists', form.errors['admission_number'][0])


class StudentViewTests(TestCase):
    """
    Functional and integration tests for HTML pages and CRUD workflows.
    """

    def setUp(self):
        self.client = Client()
        self.student1 = Student.objects.create(
            student_name="Fatima Noor",
            admission_number="ADM-010",
            student_class="Class 6",
            contact_number="03001112233"
        )
        self.student2 = Student.objects.create(
            student_name="Bilal Tariq",
            admission_number="ADM-020",
            student_class="Class 7",
            contact_number="03004445566"
        )

    def test_dashboard_view_and_count(self):
        """FR-01: Dashboard shows accurate total student count."""
        response = self.client.get(reverse('students:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'students/dashboard.html')
        self.assertEqual(response.context['total_students'], 2)
        self.assertContains(response, 'Total Enrolled Students')
        self.assertContains(response, 'Fatima Noor')
        self.assertContains(response, 'Bilal Tariq')

    def test_student_list_view(self):
        """FR-05 & TC-04: View Students shows all saved student records with 4 fields."""
        response = self.client.get(reverse('students:student_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'students/student_list.html')
        self.assertContains(response, 'Fatima Noor')
        self.assertContains(response, 'ADM-010')
        self.assertContains(response, 'Class 6')
        self.assertContains(response, '03001112233')

    def test_student_list_search_query(self):
        """Search filter isolates matched students."""
        response = self.client.get(reverse('students:student_list'), {'q': 'Fatima'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Fatima Noor')
        self.assertNotContains(response, 'Bilal Tariq')

    def test_add_student_get_form(self):
        """FR-02: Add student form renders on GET."""
        response = self.client.get(reverse('students:student_add'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'students/student_form.html')
        self.assertIn('form', response.context)

    def test_add_student_post_valid(self):
        """TC-01: Valid POST creates student and redirects to student directory."""
        post_data = {
            'student_name': 'Hamza Sheikh',
            'admission_number': 'ADM-030',
            'student_class': 'Class 9',
            'contact_number': '03335556677'
        }
        response = self.client.post(reverse('students:student_add'), data=post_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Student.objects.filter(admission_number='ADM-030').exists())
        self.assertContains(response, 'Hamza Sheikh')
        self.assertContains(response, 'registered successfully')

    def test_add_student_post_invalid(self):
        """TC-02: Missing required field does not save record and shows error."""
        post_data = {
            'student_name': 'Incomplete Student',
            'admission_number': '',  # missing!
            'student_class': 'Class 9',
            'contact_number': '03335556677'
        }
        initial_count = Student.objects.count()
        response = self.client.post(reverse('students:student_add'), data=post_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Student.objects.count(), initial_count)
        self.assertFormError(response.context['form'], 'admission_number', 'Admission number is required.')

    def test_edit_student_view_and_update(self):
        """TC-05 & FR-06: Edit student form displays existing data and updates correctly."""
        edit_url = reverse('students:student_edit', args=[self.student1.id])
        
        # Test GET loads current info
        get_resp = self.client.get(edit_url)
        self.assertEqual(get_resp.status_code, 200)
        self.assertEqual(get_resp.context['form'].initial['student_name'], 'Fatima Noor')

        # Test POST saves changes
        update_data = {
            'student_name': 'Fatima Noor Updated',
            'admission_number': 'ADM-010',
            'student_class': 'Class 7-A',
            'contact_number': '03009998877',
        }
        post_resp = self.client.post(edit_url, data=update_data, follow=True)
        self.assertEqual(post_resp.status_code, 200)
        self.student1.refresh_from_db()
        self.assertEqual(self.student1.student_name, 'Fatima Noor Updated')
        self.assertEqual(self.student1.student_class, 'Class 7-A')
        self.assertEqual(self.student1.contact_number, '03009998877')

    def test_delete_student_confirmation_page_get_does_not_delete(self):
        """TC-06: GET confirmation page does NOT delete the record."""
        delete_url = reverse('students:student_delete', args=[self.student2.id])
        response = self.client.get(delete_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'students/student_confirm_delete.html')
        # Ensure student is still in DB
        self.assertTrue(Student.objects.filter(id=self.student2.id).exists())

    def test_delete_student_post_confirms_and_deletes(self):
        """TC-07: POST deletion request permanently deletes the record."""
        delete_url = reverse('students:student_delete', args=[self.student2.id])
        response = self.client.post(delete_url, follow=True)
        self.assertEqual(response.status_code, 200)
        # Ensure student was removed from DB
        self.assertFalse(Student.objects.filter(id=self.student2.id).exists())
        self.assertContains(response, 'was permanently removed')


class StudentRestApiTests(TestCase):
    """
    Tests for the optional JSON REST API endpoints specified in API Specification.
    """

    def setUp(self):
        self.client = Client()
        self.student = Student.objects.create(
            student_name="API Test Student",
            admission_number="ADM-API-1",
            student_class="Grade 11",
            contact_number="03120000000"
        )

    def test_api_list_students(self):
        """GET /api/students/ returns 200 and list of students."""
        response = self.client.get(reverse('students:api_student_list_create'))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['admission_number'], 'ADM-API-1')

    def test_api_create_student_valid(self):
        """POST /api/students/ creates student and returns 201."""
        payload = {
            'student_name': 'New API Enrollee',
            'admission_number': 'ADM-API-2',
            'student_class': 'Grade 12',
            'contact_number': '03130000000'
        }
        response = self.client.post(
            reverse('students:api_student_list_create'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.content)
        self.assertEqual(data['student_name'], 'New API Enrollee')
        self.assertTrue(Student.objects.filter(admission_number='ADM-API-2').exists())

    def test_api_create_student_duplicate_admission(self):
        """POST duplicate admission returns 400 Bad Request."""
        payload = {
            'student_name': 'Dupe Enrollee',
            'admission_number': 'ADM-API-1',
            'student_class': 'Grade 10',
            'contact_number': '03140000000'
        }
        response = self.client.post(
            reverse('students:api_student_list_create'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn('admission_number', data['errors'])

    def test_api_get_detail_and_404(self):
        """GET /api/students/<id>/ returns single object or 404."""
        response = self.client.get(reverse('students:api_student_detail', args=[self.student.id]))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['id'], self.student.id)

        # Non-existent ID
        resp_404 = self.client.get(reverse('students:api_student_detail', args=[99999]))
        self.assertEqual(resp_404.status_code, 404)

    def test_api_patch_student(self):
        """PATCH /api/students/<id>/ updates fields."""
        payload = {'student_class': 'Grade 11-Honors'}
        response = self.client.patch(
            reverse('students:api_student_detail', args=[self.student.id]),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.student.refresh_from_db()
        self.assertEqual(self.student.student_class, 'Grade 11-Honors')

    def test_api_delete_student(self):
        """DELETE /api/students/<id>/ returns 204 No Content."""
        response = self.client.delete(reverse('students:api_student_detail', args=[self.student.id]))
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Student.objects.filter(id=self.student.id).exists())
