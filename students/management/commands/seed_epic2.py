import datetime
from django.core.management.base import BaseCommand
from students.models import Student
from teachers.models import Teacher
from fees.models import FeeRecord
from attendance.models import AttendanceRecord


class Command(BaseCommand):
    help = 'Seeds sample data for Epic 2: Teachers, Fees, and Attendance'

    def handle(self, *args, **options):
        # ── Teachers ──────────────────────────────
        teachers_data = [
            {'employee_id': 'TCH-001', 'full_name': 'Mr. Ahsan Ali', 'phone': '03001111111',
             'department': 'Mathematics', 'subject': 'Mathematics', 'assigned_class': 'Class 8-A, Class 9-A',
             'qualification': 'M.Sc Mathematics, B.Ed', 'date_joined': datetime.date(2020, 1, 15), 'status': 'Active'},
            {'employee_id': 'TCH-002', 'full_name': 'Ms. Sana Fatima', 'phone': '03002222222',
             'department': 'English', 'subject': 'English Literature', 'assigned_class': 'Class 9-B, Class 10-A',
             'qualification': 'MA English, B.Ed', 'date_joined': datetime.date(2019, 8, 1), 'status': 'Active'},
            {'employee_id': 'TCH-003', 'full_name': 'Mr. Tariq Hassan', 'phone': '03003333333',
             'department': 'Science', 'subject': 'Physics', 'assigned_class': 'Class 10-A, Class 10-B',
             'qualification': 'M.Sc Physics', 'date_joined': datetime.date(2021, 3, 20), 'status': 'Active'},
            {'employee_id': 'TCH-004', 'full_name': 'Ms. Nadia Zubair', 'phone': '03004444444',
             'department': 'Urdu', 'subject': 'Urdu', 'assigned_class': 'Class 7-A, Class 8-B',
             'qualification': 'MA Urdu', 'date_joined': datetime.date(2018, 6, 10), 'status': 'On Leave'},
            {'employee_id': 'TCH-005', 'full_name': 'Mr. Kamran Iqbal', 'phone': '03005555555',
             'department': 'Computer Science', 'subject': 'Computer Science', 'assigned_class': 'Class 9-A, Class 10-B',
             'qualification': 'BS Computer Science', 'date_joined': datetime.date(2022, 9, 1), 'status': 'Active'},
        ]
        t_count = 0
        for td in teachers_data:
            obj, created = Teacher.objects.get_or_create(employee_id=td['employee_id'], defaults=td)
            if created:
                t_count += 1

        # ── Fees ──────────────────────────────────
        students = list(Student.objects.all()[:5])
        today = datetime.date.today()
        fee_count = 0
        for i, student in enumerate(students):
            records = [
                {'fee_type': 'Monthly Tuition', 'amount_due': 3500, 'amount_paid': 3500,
                 'status': 'Paid', 'month': today.month, 'year': today.year,
                 'due_date': today.replace(day=5), 'payment_date': today.replace(day=3)},
                {'fee_type': 'Exam Fee', 'amount_due': 1500,
                 'amount_paid': 0 if i % 2 == 0 else 1500,
                 'status': 'Unpaid' if i % 2 == 0 else 'Paid',
                 'month': today.month, 'year': today.year,
                 'due_date': today.replace(day=15), 'payment_date': None},
            ]
            for rd in records:
                _, created = FeeRecord.objects.get_or_create(
                    student=student,
                    fee_type=rd['fee_type'],
                    month=rd['month'],
                    year=rd['year'],
                    defaults={'amount_due': rd['amount_due'], 'amount_paid': rd['amount_paid'],
                              'status': rd['status'], 'due_date': rd['due_date'],
                              'payment_date': rd.get('payment_date')}
                )
                if created:
                    fee_count += 1

        # ── Attendance ────────────────────────────
        att_count = 0
        statuses = ['Present', 'Present', 'Present', 'Absent', 'Late']
        all_students = list(Student.objects.all())
        for day_offset in range(7):
            att_date = today - datetime.timedelta(days=day_offset)
            if att_date.weekday() >= 5:   # skip weekends
                continue
            for idx, student in enumerate(all_students):
                status = statuses[(idx + day_offset) % len(statuses)]
                _, created = AttendanceRecord.objects.get_or_create(
                    student=student,
                    date=att_date,
                    defaults={'status': status, 'marked_by': 'Admin (Seed)'}
                )
                if created:
                    att_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'Epic 2 seed complete: {t_count} teachers, {fee_count} fee records, {att_count} attendance records.'
        ))
