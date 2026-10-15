import datetime
from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.core.exceptions import ValidationError
from students.models import Student
from teachers.models import Teacher
from exams.models import Subject, Exam, ExamSchedule, Mark
from announcements.models import Announcement


class SubjectModelAndViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.teacher = Teacher.objects.create(
            full_name="Prof. Alan Turing",
            employee_id="TCH-999",
            email="alan@turing.edu",
            phone="03001112233",
            department="Mathematics",
            subject="Mathematics",
            date_joined=datetime.date.today(),
            status="Active"
        )
        self.subject = Subject.objects.create(
            name="Computer Science",
            code="CS-101",
            class_grade="Class 8",
            teacher=self.teacher,
            description="Foundations of Computer Science"
        )

    def test_subject_model_str_and_clean(self):
        self.assertEqual(str(self.subject), "Computer Science (CS-101)")
        subj2 = Subject(name="  Physics  ", code="  phy-201  ")
        subj2.clean()
        self.assertEqual(subj2.name, "Physics")
        self.assertEqual(subj2.code, "PHY-201")

    def test_subject_list_view(self):
        response = self.client.get(reverse('exams:subject_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Computer Science")
        self.assertContains(response, "CS-101")

    def test_subject_list_search(self):
        response = self.client.get(reverse('exams:subject_list') + '?q=Computer')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "CS-101")

        response_none = self.client.get(reverse('exams:subject_list') + '?q=NonExistentSubject')
        self.assertEqual(response_none.status_code, 200)
        self.assertNotContains(response_none, "CS-101")

    def test_subject_add_view_get_and_post(self):
        get_res = self.client.get(reverse('exams:subject_add'))
        self.assertEqual(get_res.status_code, 200)

        post_res = self.client.post(reverse('exams:subject_add'), {
            'name': 'Chemistry',
            'code': 'CHM-101',
            'class_grade': 'Class 9',
            'teacher': self.teacher.id,
            'description': 'Organic & Inorganic Chemistry'
        })
        self.assertEqual(post_res.status_code, 302)
        self.assertTrue(Subject.objects.filter(code='CHM-101').exists())

    def test_subject_edit_view(self):
        edit_url = reverse('exams:subject_edit', kwargs={'pk': self.subject.pk})
        res = self.client.get(edit_url)
        self.assertEqual(res.status_code, 200)

        post_res = self.client.post(edit_url, {
            'name': 'Advanced Computer Science',
            'code': 'CS-101',
            'class_grade': 'Class 8',
            'teacher': self.teacher.id,
            'description': 'Updated'
        })
        self.assertEqual(post_res.status_code, 302)
        self.subject.refresh_from_db()
        self.assertEqual(self.subject.name, 'Advanced Computer Science')

    def test_subject_delete_view(self):
        del_url = reverse('exams:subject_delete', kwargs={'pk': self.subject.pk})
        get_res = self.client.get(del_url)
        self.assertEqual(get_res.status_code, 200)

        post_res = self.client.post(del_url)
        self.assertEqual(post_res.status_code, 302)
        self.assertFalse(Subject.objects.filter(pk=self.subject.pk).exists())


class ExamModelAndViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        today = datetime.date.today()
        self.exam = Exam.objects.create(
            name="Midterm Exam 2026",
            exam_type="midterm",
            academic_year="2025-2026",
            term="Semester 1",
            start_date=today,
            end_date=today + datetime.timedelta(days=7),
            is_published=True,
            description="Midterm evaluation"
        )

    def test_exam_str(self):
        self.assertEqual(str(self.exam), "Midterm Exam 2026 (2025-2026)")

    def test_exam_date_validation(self):
        today = datetime.date.today()
        invalid_exam = Exam(
            name="Invalid Dates",
            exam_type="quiz",
            start_date=today,
            end_date=today - datetime.timedelta(days=2)
        )
        with self.assertRaises(ValidationError):
            invalid_exam.clean()

    def test_exam_list_view_and_filters(self):
        response = self.client.get(reverse('exams:exam_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Midterm Exam 2026")

        filter_res = self.client.get(reverse('exams:exam_list') + '?type=midterm')
        self.assertEqual(filter_res.status_code, 200)
        self.assertContains(filter_res, "Midterm Exam 2026")

        filter_mismatch = self.client.get(reverse('exams:exam_list') + '?type=final')
        self.assertNotContains(filter_mismatch, "Midterm Exam 2026")

    def test_exam_add_view(self):
        today = datetime.date.today()
        post_res = self.client.post(reverse('exams:exam_add'), {
            'name': 'Final Exam 2026',
            'exam_type': 'final',
            'academic_year': '2025-2026',
            'term': 'Semester 2',
            'start_date': (today + datetime.timedelta(days=30)).strftime('%Y-%m-%d'),
            'end_date': (today + datetime.timedelta(days=40)).strftime('%Y-%m-%d'),
            'is_published': True,
            'description': 'Annual finals'
        })
        self.assertEqual(post_res.status_code, 302)
        self.assertTrue(Exam.objects.filter(name='Final Exam 2026').exists())

    def test_exam_edit_and_delete(self):
        edit_url = reverse('exams:exam_edit', kwargs={'pk': self.exam.pk})
        post_res = self.client.post(edit_url, {
            'name': 'Updated Midterm Exam 2026',
            'exam_type': self.exam.exam_type,
            'academic_year': self.exam.academic_year,
            'term': self.exam.term,
            'start_date': self.exam.start_date.strftime('%Y-%m-%d'),
            'end_date': self.exam.end_date.strftime('%Y-%m-%d'),
            'is_published': False,
        })
        self.assertEqual(post_res.status_code, 302)
        self.exam.refresh_from_db()
        self.assertEqual(self.exam.name, 'Updated Midterm Exam 2026')

        del_url = reverse('exams:exam_delete', kwargs={'pk': self.exam.pk})
        del_res = self.client.post(del_url)
        self.assertEqual(del_res.status_code, 302)
        self.assertFalse(Exam.objects.filter(pk=self.exam.pk).exists())


class MarkModelAndViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        today = datetime.date.today()
        self.student = Student.objects.create(
            student_name="Hamza Tariq",
            admission_number="ADM-888",
            student_class="Class 8",
            contact_number="03001234567"
        )
        self.subject = Subject.objects.create(
            name="Mathematics",
            code="MTH-800",
            class_grade="Class 8"
        )
        self.exam = Exam.objects.create(
            name="Term 1 Exam",
            exam_type="midterm",
            start_date=today,
            end_date=today + datetime.timedelta(days=5)
        )
        self.mark = Mark.objects.create(
            exam=self.exam,
            student=self.student,
            subject=self.subject,
            marks_obtained=Decimal('85.50'),
            total_marks=Decimal('100.00'),
            remarks="Excellent analytical skills"
        )

    def test_automated_grade_calculation(self):
        # 85.5% should be grade A
        self.assertEqual(self.mark.percentage, 85.5)
        self.assertEqual(self.mark.grade, "A")
        self.assertTrue(self.mark.is_passed)

        # Test A+
        self.mark.marks_obtained = Decimal('95.0')
        self.mark.save()
        self.assertEqual(self.mark.grade, "A+")

        # Test B
        self.mark.marks_obtained = Decimal('72.0')
        self.mark.save()
        self.assertEqual(self.mark.grade, "B")

        # Test C
        self.mark.marks_obtained = Decimal('62.0')
        self.mark.save()
        self.assertEqual(self.mark.grade, "C")

        # Test D
        self.mark.marks_obtained = Decimal('52.0')
        self.mark.save()
        self.assertEqual(self.mark.grade, "D")

        # Test E
        self.mark.marks_obtained = Decimal('42.0')
        self.mark.save()
        self.assertEqual(self.mark.grade, "E")

        # Test F
        self.mark.marks_obtained = Decimal('25.0')
        self.mark.save()
        self.assertEqual(self.mark.grade, "F")
        self.assertFalse(self.mark.is_passed)

    def test_mark_validation(self):
        invalid_mark_negative = Mark(
            exam=self.exam,
            student=self.student,
            subject=self.subject,
            marks_obtained=Decimal('-5.0'),
            total_marks=Decimal('100.0')
        )
        with self.assertRaises(ValidationError):
            invalid_mark_negative.clean()

        invalid_mark_exceeds = Mark(
            exam=self.exam,
            student=self.student,
            subject=self.subject,
            marks_obtained=Decimal('115.0'),
            total_marks=Decimal('100.0')
        )
        with self.assertRaises(ValidationError):
            invalid_mark_exceeds.clean()

    def test_marks_list_view_and_filters(self):
        res = self.client.get(reverse('exams:marks_list'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Hamza Tariq")
        self.assertContains(res, "Mathematics")

        res_exam_filter = self.client.get(reverse('exams:marks_list') + f'?exam={self.exam.id}')
        self.assertEqual(res_exam_filter.status_code, 200)
        self.assertContains(res_exam_filter, "Hamza Tariq")

    def test_mark_add_edit_delete(self):
        s2 = Student.objects.create(student_name="Sara Ahmed", admission_number="ADM-889", student_class="Class 8", contact_number="03001112233")
        post_res = self.client.post(reverse('exams:mark_add'), {
            'exam': self.exam.id,
            'student': s2.id,
            'subject': self.subject.id,
            'marks_obtained': '78.0',
            'total_marks': '100.0',
            'remarks': 'Good'
        })
        self.assertEqual(post_res.status_code, 302)
        self.assertTrue(Mark.objects.filter(student=s2, subject=self.subject).exists())

        mark_obj = Mark.objects.get(student=s2, subject=self.subject)
        edit_res = self.client.post(reverse('exams:mark_edit', kwargs={'pk': mark_obj.pk}), {
            'exam': self.exam.id,
            'student': s2.id,
            'subject': self.subject.id,
            'marks_obtained': '91.0',
            'total_marks': '100.0',
            'remarks': 'Upgraded'
        })
        self.assertEqual(edit_res.status_code, 302)
        mark_obj.refresh_from_db()
        self.assertEqual(mark_obj.grade, 'A+')

        del_res = self.client.post(reverse('exams:mark_delete', kwargs={'pk': mark_obj.pk}))
        self.assertEqual(del_res.status_code, 302)
        self.assertFalse(Mark.objects.filter(pk=mark_obj.pk).exists())

    def test_bulk_marks_entry(self):
        # GET class roster
        url = reverse('exams:bulk_marks_entry') + f'?exam={self.exam.id}&subject={self.subject.id}&student_class=Class 8'
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Hamza Tariq")

        # POST bulk update
        post_data = {
            'exam_id': self.exam.id,
            'subject_id': self.subject.id,
            'student_class': 'Class 8',
            'total_marks': '100',
            f'marks_{self.student.id}': '89.5',
            f'remarks_{self.student.id}': 'Bulk updated remark'
        }
        post_res = self.client.post(reverse('exams:bulk_marks_entry'), post_data)
        self.assertEqual(post_res.status_code, 302)
        self.mark.refresh_from_db()
        self.assertEqual(self.mark.marks_obtained, Decimal('89.5'))

    def test_student_report_card(self):
        url = reverse('exams:student_report_card', kwargs={'student_id': self.student.id})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Hamza Tariq")
        self.assertContains(res, "Academic Transcript")
        self.assertContains(res, "Official Transcript")


class AnnouncementModelAndViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        today = datetime.date.today()
        self.notice = Announcement.objects.create(
            title="School Annual Sports Gala 2026",
            category="sports",
            content="Detailed rules and schedule for sports gala week.",
            audience="all",
            priority="high",
            is_pinned=True,
            is_active=True,
            published_date=today
        )

    def test_announcement_str(self):
        self.assertIn("School Annual Sports Gala 2026", str(self.notice))

    def test_announcement_list_and_filters(self):
        res = self.client.get(reverse('announcements:announcement_list'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "School Annual Sports Gala 2026")

        res_cat = self.client.get(reverse('announcements:announcement_list') + '?category=sports')
        self.assertContains(res_cat, "Sports Gala")

        res_wrong_cat = self.client.get(reverse('announcements:announcement_list') + '?category=holiday')
        self.assertNotContains(res_wrong_cat, "Sports Gala")

    def test_announcement_detail_view(self):
        url = reverse('announcements:announcement_detail', kwargs={'pk': self.notice.pk})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "School Annual Sports Gala 2026")
        self.assertContains(res, "Detailed rules and schedule")

    def test_announcement_create_edit_delete(self):
        today = datetime.date.today()
        post_res = self.client.post(reverse('announcements:announcement_add'), {
            'title': 'Midterm Result Announcement',
            'category': 'academic',
            'content': 'Results have been released.',
            'audience': 'students',
            'priority': 'urgent',
            'published_date': today.strftime('%Y-%m-%d'),
            'is_active': True,
        })
        self.assertEqual(post_res.status_code, 302)
        self.assertTrue(Announcement.objects.filter(title='Midterm Result Announcement').exists())

        notice2 = Announcement.objects.get(title='Midterm Result Announcement')
        edit_res = self.client.post(reverse('announcements:announcement_edit', kwargs={'pk': notice2.pk}), {
            'title': 'Updated Midterm Results',
            'category': 'academic',
            'content': 'Updated content.',
            'audience': 'all',
            'priority': 'normal',
            'published_date': today.strftime('%Y-%m-%d'),
            'is_active': True,
        })
        self.assertEqual(edit_res.status_code, 302)
        notice2.refresh_from_db()
        self.assertEqual(notice2.title, 'Updated Midterm Results')

        del_res = self.client.post(reverse('announcements:announcement_delete', kwargs={'pk': notice2.pk}))
        self.assertEqual(del_res.status_code, 302)
        self.assertFalse(Announcement.objects.filter(pk=notice2.pk).exists())


class DashboardEpic3IntegrationTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_dashboard_renders_epic3_stats(self):
        res = self.client.get(reverse('students:dashboard'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Examinations")
        self.assertContains(res, "Operational")
