import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from .models import AttendanceRecord
from .forms import AttendanceDateForm, AttendanceRecordForm
from students.models import Student


def attendance_list_view(request):
    """View/filter attendance records by date, class, or student."""
    date_filter = request.GET.get('date', '').strip()
    class_filter = request.GET.get('class', '').strip()
    status_filter = request.GET.get('status', '').strip()
    query = request.GET.get('q', '').strip()

    records = AttendanceRecord.objects.select_related('student').order_by('-date', 'student__student_name')

    if date_filter:
        try:
            records = records.filter(date=datetime.date.fromisoformat(date_filter))
        except ValueError:
            pass
    if class_filter:
        records = records.filter(student__student_class__iexact=class_filter)
    if status_filter:
        records = records.filter(status=status_filter)
    if query:
        records = records.filter(
            Q(student__student_name__icontains=query) |
            Q(student__admission_number__icontains=query)
        )

    total = records.count()
    present_count = records.filter(status='Present').count()
    absent_count  = records.filter(status='Absent').count()
    late_count    = records.filter(status='Late').count()

    paginator = Paginator(records, 15)
    page_obj  = paginator.get_page(request.GET.get('page', 1))

    all_classes = Student.objects.values_list('student_class', flat=True).distinct().order_by('student_class')

    context = {
        'page_title': 'Attendance Records',
        'active_tab': 'attendance',
        'page_obj': page_obj,
        'query': query,
        'date_filter': date_filter,
        'class_filter': class_filter,
        'status_filter': status_filter,
        'total': total,
        'present_count': present_count,
        'absent_count': absent_count,
        'late_count': late_count,
        'all_classes': all_classes,
        'status_choices': AttendanceRecord.STATUS_CHOICES,
        'today': datetime.date.today().isoformat(),
    }
    return render(request, 'attendance/attendance_list.html', context)


def attendance_mark_view(request):
    """
    Bulk-mark attendance for all students of a selected class on a given date.
    GET: Show date/class selector form.
    POST step 1: Show list of students for that class.
    POST step 2 (mark): Save all attendance records.
    """
    all_classes = [(c, c) for c in
                   Student.objects.values_list('student_class', flat=True).distinct().order_by('student_class')]

    if request.method == 'POST' and 'mark_attendance' in request.POST:
        # Step 2: Save submitted statuses
        date_str = request.POST.get('att_date')
        student_ids = request.POST.getlist('student_ids')
        marked_by = request.POST.get('marked_by', '').strip()
        saved = 0
        try:
            att_date = datetime.date.fromisoformat(date_str)
        except (ValueError, TypeError):
            messages.error(request, 'Invalid date submitted.')
            return redirect('attendance:attendance_mark')

        for sid in student_ids:
            student = Student.objects.filter(id=sid).first()
            if not student:
                continue
            status = request.POST.get(f'status_{sid}', 'Present')
            remarks = request.POST.get(f'remarks_{sid}', '').strip()
            AttendanceRecord.objects.update_or_create(
                student=student,
                date=att_date,
                defaults={
                    'status': status,
                    'remarks': remarks,
                    'marked_by': marked_by,
                }
            )
            saved += 1
        messages.success(request, f"Attendance marked for {saved} students on {att_date.strftime('%b %d, %Y')}!")
        return redirect('attendance:attendance_list')

    # Step 1: Filter by class + date
    selected_class = request.POST.get('student_class', '') if request.method == 'POST' else ''
    selected_date = request.POST.get('date', datetime.date.today().isoformat()) if request.method == 'POST' else datetime.date.today().isoformat()

    selector_form = AttendanceDateForm(
        request.POST if request.method == 'POST' else None,
        class_choices=all_classes
    )

    students_to_mark = []
    existing_map = {}

    if request.method == 'POST' and selector_form.is_valid():
        selected_class = selector_form.cleaned_data['student_class']
        selected_date  = selector_form.cleaned_data['date'].isoformat()
        students_to_mark = Student.objects.filter(student_class__iexact=selected_class).order_by('student_name')

        # Pre-load existing records for that date to pre-fill the form
        try:
            d = datetime.date.fromisoformat(selected_date)
            existing = AttendanceRecord.objects.filter(date=d, student__in=students_to_mark)
            existing_map = {r.student_id: r for r in existing}
        except ValueError:
            pass

    context = {
        'page_title': 'Mark Attendance',
        'active_tab': 'attendance',
        'selector_form': selector_form,
        'students_to_mark': students_to_mark,
        'existing_map': existing_map,
        'selected_class': selected_class,
        'selected_date': selected_date,
        'status_choices': AttendanceRecord.STATUS_CHOICES,
    }
    return render(request, 'attendance/attendance_mark.html', context)


def attendance_edit_view(request, id):
    record = get_object_or_404(AttendanceRecord, id=id)
    if request.method == 'POST':
        form = AttendanceRecordForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            messages.success(request, f"Attendance record updated for '{record.student.student_name}'.")
            return redirect('attendance:attendance_list')
        messages.error(request, "Please correct the errors below.")
    else:
        form = AttendanceRecordForm(instance=record)

    context = {
        'page_title': 'Edit Attendance Record',
        'active_tab': 'attendance',
        'form': form,
        'record': record,
    }
    return render(request, 'attendance/attendance_edit.html', context)


def attendance_delete_view(request, id):
    record = get_object_or_404(AttendanceRecord, id=id)
    if request.method == 'POST':
        name = record.student.student_name
        date = record.date
        record.delete()
        messages.success(request, f"Attendance record for '{name}' on {date} deleted.")
        return redirect('attendance:attendance_list')
    context = {
        'page_title': 'Confirm Delete Attendance Record',
        'active_tab': 'attendance',
        'record': record,
    }
    return render(request, 'attendance/attendance_confirm_delete.html', context)


def attendance_student_report_view(request, student_id):
    """Summary attendance report for a specific student."""
    student = get_object_or_404(Student, id=student_id)
    records = AttendanceRecord.objects.filter(student=student).order_by('-date')
    total   = records.count()
    present = records.filter(status='Present').count()
    absent  = records.filter(status='Absent').count()
    late    = records.filter(status='Late').count()
    leave   = records.filter(status='Leave').count()
    pct     = round((present / total) * 100, 1) if total > 0 else 0

    context = {
        'page_title': f'Attendance Report — {student.student_name}',
        'active_tab': 'attendance',
        'student': student,
        'records': records[:30],
        'total': total,
        'present': present,
        'absent': absent,
        'late': late,
        'leave': leave,
        'pct': pct,
    }
    return render(request, 'attendance/attendance_student_report.html', context)
