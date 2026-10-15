import datetime
from decimal import Decimal
from django.core.management.base import BaseCommand
from students.models import Student
from teachers.models import Teacher
from exams.models import Subject, Exam, ExamSchedule, Mark
from announcements.models import Announcement


class Command(BaseCommand):
    help = 'Seeds sample data for Epic 3: Subjects, Exams, Marks, Schedules, and Notice Board Announcements'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE("Seeding Epic 3: Examinations, Subjects, Marks, and Announcements..."))

        # 1. Teachers link for subjects
        teachers = list(Teacher.objects.all())
        t_math = teachers[0] if len(teachers) > 0 else None
        t_eng = teachers[1] if len(teachers) > 1 else None
        t_sci = teachers[2] if len(teachers) > 2 else None
        t_cs = teachers[3] if len(teachers) > 3 else None

        # 2. Subjects
        subjects_data = [
            {'name': 'Mathematics', 'code': 'MTH-101', 'class_grade': 'All', 'teacher': t_math, 'description': 'Algebra, Geometry, Trigonometry, and Calculus fundamentals.'},
            {'name': 'English Language & Lit', 'code': 'ENG-102', 'class_grade': 'All', 'teacher': t_eng, 'description': 'Grammar, Reading comprehension, essay writing, and literature.'},
            {'name': 'Computer Science', 'code': 'CS-201', 'class_grade': 'Class 8', 'teacher': t_cs, 'description': 'Python programming, data structures, and computer networks.'},
            {'name': 'General Science', 'code': 'SCI-103', 'class_grade': 'Class 8', 'teacher': t_sci, 'description': 'Physics, Chemistry, and Biology introductory concepts.'},
            {'name': 'Pakistan & Islamic Studies', 'code': 'PST-104', 'class_grade': 'All', 'teacher': None, 'description': 'History, cultural heritage, ethics, and civil studies.'},
        ]

        created_subjects = []
        for sdata in subjects_data:
            subj, created = Subject.objects.update_or_create(
                code=sdata['code'],
                defaults=sdata
            )
            created_subjects.append(subj)

        # 3. Exams
        today = datetime.date.today()
        exams_data = [
            {
                'name': 'Midterm Examination 2026',
                'exam_type': 'midterm',
                'academic_year': '2025-2026',
                'term': 'First Semester',
                'start_date': today - datetime.timedelta(days=20),
                'end_date': today - datetime.timedelta(days=10),
                'is_published': True,
                'description': 'Official comprehensive midterm examinations for all active classes.',
            },
            {
                'name': 'Final Annual Assessment 2026',
                'exam_type': 'final',
                'academic_year': '2025-2026',
                'term': 'Annual Term',
                'start_date': today + datetime.timedelta(days=45),
                'end_date': today + datetime.timedelta(days=60),
                'is_published': True,
                'description': 'End of year promotional board examination.',
            },
            {
                'name': 'Monthly Unit Quiz #2',
                'exam_type': 'quiz',
                'academic_year': '2025-2026',
                'term': 'Monthly Test',
                'start_date': today - datetime.timedelta(days=5),
                'end_date': today - datetime.timedelta(days=2),
                'is_published': True,
                'description': 'Continuous diagnostic assessment for class progression.',
            },
        ]

        created_exams = []
        for edata in exams_data:
            ex, _ = Exam.objects.update_or_create(
                name=edata['name'],
                defaults=edata
            )
            created_exams.append(ex)

        primary_exam = created_exams[0]

        # 4. Marks for all existing students
        students = list(Student.objects.all())
        marks_count = 0

        # Sample score distributions
        scores_matrix = [
            (Decimal('92.5'), 'Outstanding analytical mastery'),
            (Decimal('85.0'), 'Excellent performance and comprehension'),
            (Decimal('78.5'), 'Very good work, consistent participation'),
            (Decimal('68.0'), 'Good effort, needs revision in problem solving'),
            (Decimal('54.5'), 'Average standing, requires targeted practice'),
            (Decimal('88.0'), 'High distinction in homework and practicals'),
            (Decimal('42.0'), 'Borderline pass, recommended for after-school tutoring'),
        ]

        for s_idx, student in enumerate(students):
            for subj_idx, subj in enumerate(created_subjects):
                # Pick score with slight offset
                score_item = scores_matrix[(s_idx + subj_idx) % len(scores_matrix)]
                obtained, remark = score_item

                m, created = Mark.objects.update_or_create(
                    exam=primary_exam,
                    student=student,
                    subject=subj,
                    defaults={
                        'marks_obtained': obtained,
                        'total_marks': Decimal('100.00'),
                        'remarks': remark,
                    }
                )
                marks_count += 1

        # 5. Announcements
        announcements_data = [
            {
                'title': 'Midterm Examination Results & Report Cards Published',
                'category': 'academic',
                'audience': 'all',
                'priority': 'urgent',
                'is_pinned': True,
                'is_active': True,
                'published_date': today - datetime.timedelta(days=1),
                'content': 'The official results for Midterm Examination 2026 have been evaluated and published to the academic portal. Students and guardians can inspect subject breakdown, aggregate percentage, and overall grade status. Report cards are available for instant export.',
            },
            {
                'title': 'Annual Science & Robotics Exhibition 2026',
                'category': 'sports',
                'audience': 'students',
                'priority': 'high',
                'is_pinned': True,
                'is_active': True,
                'published_date': today - datetime.timedelta(days=3),
                'content': 'All students from Class 6 to 10 are invited to submit their innovative project abstracts for the upcoming Inter-School Science Fair. Registrations close this Friday at the Computer Science laboratory.',
            },
            {
                'title': 'Term Fee Submission Notice & Banking Guidelines',
                'category': 'fees',
                'audience': 'parents',
                'priority': 'normal',
                'is_pinned': False,
                'is_active': True,
                'published_date': today - datetime.timedelta(days=7),
                'content': 'Parents and guardians are kindly reminded to settle the current academic installment by the 15th of the month. Fee challans can be paid at designated partner bank branches or through the digital portal.',
            },
            {
                'title': 'Spring Break & National Holiday Observance',
                'category': 'holiday',
                'audience': 'all',
                'priority': 'normal',
                'is_pinned': False,
                'is_active': True,
                'published_date': today - datetime.timedelta(days=12),
                'content': 'The school administration campus will remain closed on Monday in observance of the declared national holiday. Normal academic routine and scheduled classes will resume promptly on Tuesday morning.',
            },
        ]

        notice_count = 0
        for ndata in announcements_data:
            Announcement.objects.update_or_create(
                title=ndata['title'],
                defaults=ndata
            )
            notice_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Epic 3 seed complete: {len(created_subjects)} subjects, {len(created_exams)} exams, "
            f"{marks_count} student mark records, {notice_count} notice board announcements."
        ))
