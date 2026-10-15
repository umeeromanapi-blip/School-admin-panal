import datetime
from django.shortcuts import render
from django.db.models import Count, Sum, Q, Avg
from students.models import Student
from teachers.models import Teacher
from fees.models import FeeRecord
from attendance.models import AttendanceRecord


def reports_overview(request):
    """
    Consolidated analytics and reporting page.
    Provides institution-wide stats, class breakdowns, and financial summaries.
    """
    today = datetime.date.today()
    current_month = today.month
    current_year = today.year

    # Student analytics
    total_students = Student.objects.count()
    students_by_class = (
        Student.objects.values('student_class')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    # Teacher analytics
    total_teachers = Teacher.objects.count()
    active_teachers = Teacher.objects.filter(status='Active').count()
    teachers_by_dept = (
        Teacher.objects.values('department')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    # Fee analytics
    total_due    = FeeRecord.objects.aggregate(t=Sum('amount_due'))['t'] or 0
    total_paid   = FeeRecord.objects.aggregate(t=Sum('amount_paid'))['t'] or 0
    total_unpaid = total_due - total_paid
    paid_records   = FeeRecord.objects.filter(status='Paid').count()
    unpaid_records = FeeRecord.objects.filter(status='Unpaid').count()
    partial_records = FeeRecord.objects.filter(status='Partial').count()
    collection_rate = round((total_paid / total_due * 100), 1) if total_due > 0 else 0

    # Fees by type
    fees_by_type = (
        FeeRecord.objects.values('fee_type')
        .annotate(total=Sum('amount_due'), paid=Sum('amount_paid'))
        .order_by('-total')
    )

    # Attendance analytics
    total_att_records = AttendanceRecord.objects.count()
    present_count  = AttendanceRecord.objects.filter(status='Present').count()
    absent_count   = AttendanceRecord.objects.filter(status='Absent').count()
    late_count     = AttendanceRecord.objects.filter(status='Late').count()
    attendance_rate = round((present_count / total_att_records * 100), 1) if total_att_records > 0 else 0

    # Today's attendance
    todays_records  = AttendanceRecord.objects.filter(date=today)
    todays_present  = todays_records.filter(status='Present').count()
    todays_absent   = todays_records.filter(status='Absent').count()
    todays_total    = todays_records.count()

    # Attendance by class (aggregate percentage)
    attendance_by_class = []
    for sc in students_by_class:
        cls = sc['student_class']
        cls_records = AttendanceRecord.objects.filter(student__student_class=cls)
        cls_total   = cls_records.count()
        cls_present = cls_records.filter(status='Present').count()
        pct = round((cls_present / cls_total * 100), 1) if cls_total > 0 else 0
        attendance_by_class.append({'class': cls, 'pct': pct, 'total': cls_total, 'student_count': sc['count']})

    context = {
        'page_title': 'Reports & Analytics',
        'active_tab': 'reports',
        'today': today,
        # Students
        'total_students': total_students,
        'students_by_class': students_by_class,
        # Teachers
        'total_teachers': total_teachers,
        'active_teachers': active_teachers,
        'teachers_by_dept': teachers_by_dept,
        # Fees
        'total_due': total_due,
        'total_paid': total_paid,
        'total_unpaid': total_unpaid,
        'paid_records': paid_records,
        'unpaid_records': unpaid_records,
        'partial_records': partial_records,
        'collection_rate': collection_rate,
        'fees_by_type': fees_by_type,
        # Attendance
        'total_att_records': total_att_records,
        'present_count': present_count,
        'absent_count': absent_count,
        'late_count': late_count,
        'attendance_rate': attendance_rate,
        'todays_present': todays_present,
        'todays_absent': todays_absent,
        'todays_total': todays_total,
        'attendance_by_class': attendance_by_class,
    }
    return render(request, 'reports/reports_overview.html', context)
