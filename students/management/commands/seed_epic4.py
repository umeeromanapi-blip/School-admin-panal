import datetime
from decimal import Decimal
from django.core.management.base import BaseCommand
from students.models import Student
from teachers.models import Teacher
from exams.models import Subject
from timetable.models import Period, TimetableEntry
from library.models import Book, BookIssue


class Command(BaseCommand):
    help = 'Seeds sample data for Epic 4: Bell Periods, Weekly Timetable Entries, Library Book Catalog, and Book Loans'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE("Seeding Epic 4: Timetable and Library Management..."))

        # 1. Periods (Bell Schedule)
        periods_data = [
            {'period_number': 1, 'name': 'Period 1 (Mathematics / Core)', 'start_time': datetime.time(8, 0), 'end_time': datetime.time(8, 45), 'is_break': False},
            {'period_number': 2, 'name': 'Period 2 (Science & Labs)', 'start_time': datetime.time(8, 45), 'end_time': datetime.time(9, 30), 'is_break': False},
            {'period_number': 3, 'name': 'Morning Recess & Refreshment', 'start_time': datetime.time(9, 30), 'end_time': datetime.time(9, 50), 'is_break': True},
            {'period_number': 4, 'name': 'Period 3 (English & Language)', 'start_time': datetime.time(9, 50), 'end_time': datetime.time(10, 35), 'is_break': False},
            {'period_number': 5, 'name': 'Period 4 (Computer Science)', 'start_time': datetime.time(10, 35), 'end_time': datetime.time(11, 20), 'is_break': False},
            {'period_number': 6, 'name': 'Lunch & Prayer Recess', 'start_time': datetime.time(11, 20), 'end_time': datetime.time(12, 0), 'is_break': True},
            {'period_number': 7, 'name': 'Period 5 (Social & Islamic Studies)', 'start_time': datetime.time(12, 0), 'end_time': datetime.time(12, 45), 'is_break': False},
            {'period_number': 8, 'name': 'Period 6 (Tutorial / Activity)', 'start_time': datetime.time(12, 45), 'end_time': datetime.time(13, 30), 'is_break': False},
        ]

        created_periods = []
        for pdata in periods_data:
            period_obj, _ = Period.objects.update_or_create(
                period_number=pdata['period_number'],
                defaults=pdata
            )
            created_periods.append(period_obj)

        # 2. Timetable Entries
        subjects = list(Subject.objects.all())
        teachers = list(Teacher.objects.filter(status__iexact='Active'))

        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        classes = ['Class 8', 'Class 9']

        slots_created = 0
        if subjects and teachers:
            # Map subjects for non-break periods
            instructional_periods = [p for p in created_periods if not p.is_break]

            for cls_name in classes:
                for d_idx, day in enumerate(days):
                    for p_idx, p in enumerate(instructional_periods):
                        subj = subjects[(d_idx + p_idx) % len(subjects)]
                        teacher = teachers[(p_idx) % len(teachers)]

                        # Check if slot already exists
                        TimetableEntry.objects.update_or_create(
                            student_class=cls_name,
                            day_of_week=day,
                            period=p,
                            defaults={
                                'subject': subj,
                                'teacher': teacher,
                                'room_number': f"Room {800 if cls_name == 'Class 8' else 900 + p_idx}",
                                'academic_year': '2025-2026',
                            }
                        )
                        slots_created += 1

        # 3. Library Books Catalog
        books_data = [
            {
                'title': 'Introduction to Algorithms (CLRS)',
                'isbn': 'ISBN-978-0262033848',
                'author': 'Thomas H. Cormen, Charles E. Leiserson',
                'category': 'Computer',
                'publisher': 'MIT Press',
                'edition': '3rd Edition',
                'total_copies': 5,
                'available_copies': 4,
                'rack_location': 'Shelf CS-01',
            },
            {
                'title': 'Concepts of Modern Physics',
                'isbn': 'ISBN-978-0072448481',
                'author': 'Arthur Beiser',
                'category': 'Science',
                'publisher': 'McGraw-Hill',
                'edition': '6th Edition',
                'total_copies': 6,
                'available_copies': 5,
                'rack_location': 'Shelf SCI-04',
            },
            {
                'title': 'Calculus: Early Transcendentals',
                'isbn': 'ISBN-978-1285741550',
                'author': 'James Stewart',
                'category': 'Mathematics',
                'publisher': 'Cengage Learning',
                'edition': '8th Edition',
                'total_copies': 4,
                'available_copies': 3,
                'rack_location': 'Shelf MTH-02',
            },
            {
                'title': 'To Kill a Mockingbird',
                'isbn': 'ISBN-978-0060935467',
                'author': 'Harper Lee',
                'category': 'Literature',
                'publisher': 'Harper Perennial',
                'edition': 'Classic Edition',
                'total_copies': 8,
                'available_copies': 7,
                'rack_location': 'Shelf LIT-05',
            },
            {
                'title': 'The Road to Mecca',
                'isbn': 'ISBN-978-1887752374',
                'author': 'Muhammad Asad',
                'category': 'Islamic',
                'publisher': 'Fons Vitae',
                'edition': 'Revised Edition',
                'total_copies': 5,
                'available_copies': 4,
                'rack_location': 'Shelf ISL-01',
            },
            {
                'title': 'A Brief History of Time',
                'isbn': 'ISBN-978-0553380163',
                'author': 'Stephen Hawking',
                'category': 'Science',
                'publisher': 'Bantam Books',
                'edition': '10th Anniversary',
                'total_copies': 6,
                'available_copies': 6,
                'rack_location': 'Shelf SCI-08',
            },
        ]

        created_books = []
        for bdata in books_data:
            book_obj, _ = Book.objects.update_or_create(
                isbn=bdata['isbn'],
                defaults=bdata
            )
            created_books.append(book_obj)

        # 4. Book Issues (Loans)
        students = list(Student.objects.all())
        today = datetime.date.today()
        loans_created = 0

        if students and len(created_books) >= 4:
            # Active normal loan
            BookIssue.objects.update_or_create(
                book=created_books[0],
                student=students[0],
                defaults={
                    'borrower_type': 'student',
                    'issue_date': today - datetime.timedelta(days=5),
                    'due_date': today + datetime.timedelta(days=9),
                    'status': 'Issued',
                    'fine_amount': Decimal('0.00'),
                    'remarks': 'Issued in pristine condition.',
                }
            )
            loans_created += 1

            # Active overdue loan
            BookIssue.objects.update_or_create(
                book=created_books[1],
                student=students[1] if len(students) > 1 else students[0],
                defaults={
                    'borrower_type': 'student',
                    'issue_date': today - datetime.timedelta(days=22),
                    'due_date': today - datetime.timedelta(days=8),
                    'status': 'Issued',
                    'fine_amount': Decimal('80.00'),
                    'remarks': 'Overdue notice sent to guardian.',
                }
            )
            loans_created += 1

            # Returned loan
            BookIssue.objects.update_or_create(
                book=created_books[2],
                student=students[2] if len(students) > 2 else students[0],
                defaults={
                    'borrower_type': 'student',
                    'issue_date': today - datetime.timedelta(days=30),
                    'due_date': today - datetime.timedelta(days=16),
                    'return_date': today - datetime.timedelta(days=14),
                    'status': 'Returned',
                    'fine_amount': Decimal('0.00'),
                    'remarks': 'Returned on time, no damages.',
                }
            )
            loans_created += 1

            # Faculty loan
            if teachers:
                BookIssue.objects.update_or_create(
                    book=created_books[4],
                    teacher=teachers[0],
                    defaults={
                        'borrower_type': 'teacher',
                        'issue_date': today - datetime.timedelta(days=7),
                        'due_date': today + datetime.timedelta(days=21),
                        'status': 'Issued',
                        'fine_amount': Decimal('0.00'),
                        'remarks': 'Faculty curriculum reference.',
                    }
                )
                loans_created += 1

        self.stdout.write(self.style.SUCCESS(
            f"Epic 4 seed complete: {len(created_periods)} bell periods, {slots_created} weekly timetable slots, "
            f"{len(created_books)} library titles, and {loans_created} borrowing loan records."
        ))
