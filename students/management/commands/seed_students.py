from django.core.management.base import BaseCommand
from students.models import Student


class Command(BaseCommand):
    help = 'Seeds sample student records for testing and demonstration'

    def handle(self, *args, **options):
        sample_students = [
            {
                'student_name': 'Ali Khan',
                'admission_number': 'ADM-001',
                'student_class': 'Class 8-A',
                'contact_number': '03001234567',
            },
            {
                'student_name': 'Sara Ahmed',
                'admission_number': 'ADM-002',
                'student_class': 'Class 9-B',
                'contact_number': '03009876543',
            },
            {
                'student_name': 'Muhammad Bilal',
                'admission_number': 'ADM-003',
                'student_class': 'Class 10-A',
                'contact_number': '03214567890',
            },
            {
                'student_name': 'Ayesha Fatima',
                'admission_number': 'ADM-004',
                'student_class': 'Class 8-B',
                'contact_number': '03331122334',
            },
            {
                'student_name': 'Zainab Tariq',
                'admission_number': 'ADM-005',
                'student_class': 'Class 7-A',
                'contact_number': '03456677889',
            },
            {
                'student_name': 'Hamza Sheikh',
                'admission_number': 'ADM-006',
                'student_class': 'Class 9-A',
                'contact_number': '03125544332',
            },
            {
                'student_name': 'Daniyal Raza',
                'admission_number': 'ADM-007',
                'student_class': 'Class 10-B',
                'contact_number': '03017788990',
            },
        ]

        count = 0
        for s in sample_students:
            obj, created = Student.objects.get_or_create(
                admission_number=s['admission_number'],
                defaults=s
            )
            if created:
                count += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully seeded {count} sample student records!'))
