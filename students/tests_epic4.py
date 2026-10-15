import datetime
from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.core.exceptions import ValidationError
from students.models import Student
from teachers.models import Teacher
from exams.models import Subject
from timetable.models import Period, TimetableEntry
from library.models import Book, BookIssue


class PeriodModelAndViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.period = Period.objects.create(
            period_number=1,
            name="Period 1 (Math)",
            start_time=datetime.time(8, 0),
            end_time=datetime.time(8, 45),
            is_break=False
        )

    def test_period_str(self):
        self.assertIn("Period 1", str(self.period))
        self.assertIn("08:00", str(self.period))

    def test_period_time_validation(self):
        invalid_p = Period(
            period_number=99,
            name="Invalid Time",
            start_time=datetime.time(10, 0),
            end_time=datetime.time(9, 30)
        )
        with self.assertRaises(ValidationError):
            invalid_p.clean()

    def test_period_list_and_add_edit_delete(self):
        # List
        res = self.client.get(reverse('timetable:period_list'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Period 1")

        # Add
        post_res = self.client.post(reverse('timetable:period_add'), {
            'period_number': 2,
            'name': 'Period 2 (Science)',
            'start_time': '08:45',
            'end_time': '09:30',
        })
        self.assertEqual(post_res.status_code, 302)
        self.assertTrue(Period.objects.filter(period_number=2).exists())

        # Edit
        p2 = Period.objects.get(period_number=2)
        edit_res = self.client.post(reverse('timetable:period_edit', kwargs={'pk': p2.pk}), {
            'period_number': 2,
            'name': 'Period 2 (Physics Lab)',
            'start_time': '08:45',
            'end_time': '09:30',
        })
        self.assertEqual(edit_res.status_code, 302)
        p2.refresh_from_db()
        self.assertEqual(p2.name, 'Period 2 (Physics Lab)')

        # Delete
        del_res = self.client.post(reverse('timetable:period_delete', kwargs={'pk': p2.pk}))
        self.assertEqual(del_res.status_code, 302)
        self.assertFalse(Period.objects.filter(period_number=2).exists())


class TimetableModelAndViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.student = Student.objects.create(
            student_name="Bilal Aslam",
            admission_number="ADM-777",
            student_class="Class 8",
            contact_number="03009988776"
        )
        self.teacher1 = Teacher.objects.create(
            full_name="Dr. Isaac Newton",
            employee_id="TCH-801",
            phone="03001234500",
            department="Science",
            subject="Physics",
            date_joined=datetime.date.today(),
            status="Active"
        )
        self.subject = Subject.objects.create(
            name="Physics",
            code="PHY-101",
            class_grade="Class 8"
        )
        self.period = Period.objects.create(
            period_number=1,
            name="Period 1",
            start_time=datetime.time(8, 0),
            end_time=datetime.time(8, 45)
        )
        self.entry = TimetableEntry.objects.create(
            student_class="Class 8",
            day_of_week="Monday",
            period=self.period,
            subject=self.subject,
            teacher=self.teacher1,
            room_number="Room 101"
        )

    def test_timetable_str(self):
        self.assertIn("Class 8", str(self.entry))
        self.assertIn("Physics", str(self.entry))

    def test_teacher_clash_detection(self):
        # Trying to assign Dr. Newton to Class 9 on the SAME day and period must raise ValidationError
        clash_entry = TimetableEntry(
            student_class="Class 9",
            day_of_week="Monday",
            period=self.period,
            subject=self.subject,
            teacher=self.teacher1,
            room_number="Room 202"
        )
        with self.assertRaises(ValidationError):
            clash_entry.clean()

    def test_class_timetable_view(self):
        res = self.client.get(reverse('timetable:class_timetable') + '?class=Class 8')
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Class Timetable")
        self.assertContains(res, "Physics")
        self.assertContains(res, "Dr. Isaac Newton")

    def test_teacher_timetable_view(self):
        res = self.client.get(reverse('timetable:teacher_timetable_detail', kwargs={'teacher_id': self.teacher1.id}))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Dr. Isaac Newton")
        self.assertContains(res, "Class 8")

    def test_entry_add_edit_delete(self):
        p2 = Period.objects.create(period_number=2, name="Period 2", start_time=datetime.time(8, 45), end_time=datetime.time(9, 30))
        # Add slot
        post_res = self.client.post(reverse('timetable:entry_add'), {
            'student_class': 'Class 8',
            'day_of_week': 'Tuesday',
            'period': p2.id,
            'subject': self.subject.id,
            'teacher': self.teacher1.id,
            'room_number': 'Room 102',
            'academic_year': '2025-2026',
        })
        self.assertEqual(post_res.status_code, 302)
        self.assertTrue(TimetableEntry.objects.filter(student_class='Class 8', day_of_week='Tuesday', period=p2).exists())

        new_entry = TimetableEntry.objects.get(student_class='Class 8', day_of_week='Tuesday', period=p2)
        # Edit slot
        edit_res = self.client.post(reverse('timetable:entry_edit', kwargs={'pk': new_entry.pk}), {
            'student_class': 'Class 8',
            'day_of_week': 'Tuesday',
            'period': p2.id,
            'subject': self.subject.id,
            'teacher': self.teacher1.id,
            'room_number': 'Lab 1',
            'academic_year': '2025-2026',
        })
        self.assertEqual(edit_res.status_code, 302)
        new_entry.refresh_from_db()
        self.assertEqual(new_entry.room_number, 'Lab 1')

        # Delete slot
        del_res = self.client.post(reverse('timetable:entry_delete', kwargs={'pk': new_entry.pk}))
        self.assertEqual(del_res.status_code, 302)
        self.assertFalse(TimetableEntry.objects.filter(pk=new_entry.pk).exists())


class BookModelAndViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.book = Book.objects.create(
            title="Clean Code",
            isbn="ISBN-978-0132350884",
            author="Robert C. Martin",
            category="Computer",
            publisher="Prentice Hall",
            total_copies=5,
            available_copies=5,
            rack_location="Shelf CS-01"
        )

    def test_book_str_and_clean(self):
        self.assertIn("Clean Code", str(self.book))
        b2 = Book(title="  Artificial Intelligence  ", isbn=" isbn-1234 ", total_copies=3, available_copies=3)
        b2.clean()
        self.assertEqual(b2.title, "Artificial Intelligence")
        self.assertEqual(b2.isbn, "ISBN-1234")

    def test_available_copies_validation(self):
        invalid_book = Book(
            title="Test Invalid Copies",
            isbn="ISBN-TEST-001",
            total_copies=3,
            available_copies=5
        )
        with self.assertRaises(ValidationError):
            invalid_book.clean()

    def test_book_catalog_list_and_filters(self):
        res = self.client.get(reverse('library:book_list'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Clean Code")

        res_cat = self.client.get(reverse('library:book_list') + '?category=Computer')
        self.assertContains(res_cat, "Clean Code")

        res_wrong_cat = self.client.get(reverse('library:book_list') + '?category=History')
        self.assertNotContains(res_wrong_cat, "Clean Code")

    def test_book_add_edit_delete(self):
        post_res = self.client.post(reverse('library:book_add'), {
            'title': 'Design Patterns',
            'isbn': 'ISBN-978-0201633610',
            'author': 'Gang of Four',
            'category': 'Computer',
            'total_copies': 4,
            'available_copies': 4,
            'rack_location': 'Shelf CS-02',
        })
        self.assertEqual(post_res.status_code, 302)
        self.assertTrue(Book.objects.filter(isbn='ISBN-978-0201633610').exists())

        b = Book.objects.get(isbn='ISBN-978-0201633610')
        edit_res = self.client.post(reverse('library:book_edit', kwargs={'pk': b.pk}), {
            'title': 'Design Patterns: Elements of Reusable OO Software',
            'isbn': b.isbn,
            'author': b.author,
            'category': b.category,
            'total_copies': 6,
            'available_copies': 6,
            'rack_location': 'Shelf CS-02',
        })
        self.assertEqual(edit_res.status_code, 302)
        b.refresh_from_db()
        self.assertEqual(b.total_copies, 6)

        del_res = self.client.post(reverse('library:book_delete', kwargs={'pk': b.pk}))
        self.assertEqual(del_res.status_code, 302)
        self.assertFalse(Book.objects.filter(pk=b.pk).exists())


class BookIssueAndReturnWorkflowTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.student = Student.objects.create(
            student_name="Zubair Ali",
            admission_number="ADM-555",
            student_class="Class 9",
            contact_number="03005554433"
        )
        self.book = Book.objects.create(
            title="Cosmos",
            isbn="ISBN-978-0345331359",
            author="Carl Sagan",
            category="Science",
            total_copies=3,
            available_copies=3,
            rack_location="Shelf SCI-01"
        )

    def test_book_issue_creation_and_copy_deduction(self):
        today = datetime.date.today()
        post_res = self.client.post(reverse('library:book_issue_create'), {
            'book': self.book.id,
            'borrower_type': 'student',
            'student': self.student.id,
            'issue_date': today.strftime('%Y-%m-%d'),
            'due_date': (today + datetime.timedelta(days=14)).strftime('%Y-%m-%d'),
            'remarks': 'Issued in good condition',
        })
        self.assertEqual(post_res.status_code, 302)
        self.assertTrue(BookIssue.objects.filter(book=self.book, student=self.student).exists())

        # Check that available_copies was decremented from 3 to 2
        self.book.refresh_from_db()
        self.assertEqual(self.book.available_copies, 2)

    def test_overdue_fine_calculation_and_return_workflow(self):
        today = datetime.date.today()
        # Create an issue that is 5 days overdue
        issue = BookIssue.objects.create(
            book=self.book,
            borrower_type='student',
            student=self.student,
            issue_date=today - datetime.timedelta(days=19),
            due_date=today - datetime.timedelta(days=5),
            status='Issued'
        )
        # Deduct copy manually to simulate issue
        self.book.available_copies = 2
        self.book.save()

        self.assertTrue(issue.is_currently_overdue)
        # 5 days overdue at PKR 10/day = PKR 50.00
        self.assertEqual(issue.calculate_fine(), Decimal('50.00'))

        # Process return
        return_res = self.client.post(reverse('library:book_return_action', kwargs={'pk': issue.pk}), {
            'return_date': today.strftime('%Y-%m-%d'),
            'fine_amount': '50.00',
            'remarks': 'Fine paid in full.',
        })
        self.assertEqual(return_res.status_code, 302)
        issue.refresh_from_db()
        self.assertEqual(issue.status, 'Returned')
        self.assertEqual(issue.fine_amount, Decimal('50.00'))

        # Check that book copy was restored from 2 back to 3
        self.book.refresh_from_db()
        self.assertEqual(self.book.available_copies, 3)


class DashboardEpic4IntegrationTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_dashboard_renders_epic4_elements(self):
        res = self.client.get(reverse('students:dashboard'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Library Books")
        self.assertContains(res, "Operational")
