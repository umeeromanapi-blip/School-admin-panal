from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from .models import Period, TimetableEntry
from .forms import PeriodForm, TimetableEntryForm
from students.models import Student
from teachers.models import Teacher


def class_timetable_view(request):
    """Interactive weekly class timetable matrix"""
    classes = Student.objects.values_list('student_class', flat=True).distinct().order_by('student_class')
    selected_class = request.GET.get('class', '')
    if not selected_class and classes:
        selected_class = classes[0]

    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    periods = Period.objects.all().order_by('period_number')

    # Build matrix: period -> { day -> entry }
    entries = TimetableEntry.objects.filter(student_class=selected_class).select_related('subject', 'teacher', 'period')
    entry_map = {}
    for e in entries:
        key = (e.period_id, e.day_of_week)
        entry_map[key] = e

    matrix_rows = []
    for p in periods:
        row_slots = []
        for d in days:
            slot = entry_map.get((p.id, d))
            row_slots.append({'day': d, 'slot': slot})
        matrix_rows.append({
            'period': p,
            'slots': row_slots,
        })

    total_classes_scheduled = TimetableEntry.objects.values('student_class').distinct().count()
    total_slots = entries.count()

    context = {
        'page_title': f'Timetable — {selected_class}' if selected_class else 'Class Timetable',
        'active_tab': 'timetable',
        'classes': classes,
        'selected_class': selected_class,
        'days': days,
        'periods': periods,
        'matrix_rows': matrix_rows,
        'total_classes_scheduled': total_classes_scheduled,
        'total_slots': total_slots,
    }
    return render(request, 'timetable/class_timetable.html', context)


def teacher_timetable_view(request, teacher_id=None):
    """Weekly schedule view for an individual teacher"""
    teachers = Teacher.objects.filter(status__iexact='Active').order_by('full_name')
    selected_teacher = None

    if teacher_id:
        selected_teacher = get_object_or_404(Teacher, pk=teacher_id)
    elif teachers:
        selected_teacher = teachers[0]

    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    periods = Period.objects.all().order_by('period_number')

    matrix_rows = []
    weekly_hours = 0
    if selected_teacher:
        entries = TimetableEntry.objects.filter(teacher=selected_teacher).select_related('subject', 'period')
        entry_map = {(e.period_id, e.day_of_week): e for e in entries}
        weekly_hours = entries.count()

        for p in periods:
            row_slots = []
            for d in days:
                slot = entry_map.get((p.id, d))
                row_slots.append({'day': d, 'slot': slot})
            matrix_rows.append({'period': p, 'slots': row_slots})

    context = {
        'page_title': f'Teacher Routine — {selected_teacher.full_name}' if selected_teacher else 'Faculty Timetable',
        'active_tab': 'teacher_timetable',
        'teachers': teachers,
        'selected_teacher': selected_teacher,
        'days': days,
        'matrix_rows': matrix_rows,
        'weekly_hours': weekly_hours,
    }
    return render(request, 'timetable/teacher_timetable.html', context)


def entry_add(request):
    """Add a timetable slot"""
    prefill_class = request.GET.get('class', '')
    prefill_day = request.GET.get('day', '')
    prefill_period = request.GET.get('period', '')

    initial = {}
    if prefill_class:
        initial['student_class'] = prefill_class
    if prefill_day:
        initial['day_of_week'] = prefill_day
    if prefill_period:
        initial['period'] = prefill_period

    if request.method == 'POST':
        form = TimetableEntryForm(request.POST)
        if form.is_valid():
            entry = form.save()
            messages.success(request, f'Slot for {entry.student_class} ({entry.day_of_week} {entry.period.name}) added!')
            return redirect(f'/timetable/?class={entry.student_class}')
        else:
            messages.error(request, 'Please resolve the scheduling conflict below.')
    else:
        form = TimetableEntryForm(initial=initial)

    return render(request, 'timetable/entry_form.html', {
        'form': form,
        'page_title': 'Add Timetable Slot',
        'active_tab': 'timetable',
        'action': 'Add',
    })


def entry_edit(request, pk):
    """Edit timetable slot"""
    entry = get_object_or_404(TimetableEntry, pk=pk)
    if request.method == 'POST':
        form = TimetableEntryForm(request.POST, instance=entry)
        if form.is_valid():
            entry = form.save()
            messages.success(request, f'Slot for {entry.student_class} updated successfully!')
            return redirect(f'/timetable/?class={entry.student_class}')
        else:
            messages.error(request, 'Please resolve the scheduling conflict below.')
    else:
        form = TimetableEntryForm(instance=entry)

    return render(request, 'timetable/entry_form.html', {
        'form': form,
        'entry': entry,
        'page_title': 'Edit Timetable Slot',
        'active_tab': 'timetable',
        'action': 'Edit',
    })


def entry_delete(request, pk):
    """Delete timetable slot"""
    entry = get_object_or_404(TimetableEntry, pk=pk)
    cls = entry.student_class
    if request.method == 'POST':
        entry.delete()
        messages.success(request, 'Timetable slot removed.')
        return redirect(f'/timetable/?class={cls}')

    return render(request, 'timetable/entry_confirm_delete.html', {
        'entry': entry,
        'page_title': 'Delete Timetable Slot',
        'active_tab': 'timetable',
    })


def period_list(request):
    """List and manage bell schedule periods"""
    periods = Period.objects.all().order_by('period_number')
    return render(request, 'timetable/period_list.html', {
        'page_title': 'Class Periods & Bell Schedule',
        'active_tab': 'timetable',
        'periods': periods,
    })


def period_add(request):
    """Add a period"""
    if request.method == 'POST':
        form = PeriodForm(request.POST)
        if form.is_valid():
            period = form.save()
            messages.success(request, f'Period {period.period_number} added.')
            return redirect('timetable:period_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PeriodForm()

    return render(request, 'timetable/period_form.html', {
        'form': form,
        'page_title': 'Add Period',
        'active_tab': 'timetable',
        'action': 'Add',
    })


def period_edit(request, pk):
    """Edit period"""
    period = get_object_or_404(Period, pk=pk)
    if request.method == 'POST':
        form = PeriodForm(request.POST, instance=period)
        if form.is_valid():
            form.save()
            messages.success(request, f'Period {period.period_number} updated.')
            return redirect('timetable:period_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PeriodForm(instance=period)

    return render(request, 'timetable/period_form.html', {
        'form': form,
        'period': period,
        'page_title': f'Edit Period {period.period_number}',
        'active_tab': 'timetable',
        'action': 'Edit',
    })


def period_delete(request, pk):
    """Delete period"""
    period = get_object_or_404(Period, pk=pk)
    if request.method == 'POST':
        p_num = period.period_number
        period.delete()
        messages.success(request, f'Period {p_num} deleted.')
        return redirect('timetable:period_list')

    return render(request, 'timetable/period_confirm_delete.html', {
        'period': period,
        'page_title': 'Delete Period',
        'active_tab': 'timetable',
    })
