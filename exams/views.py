from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q, Avg, Sum, Count
from decimal import Decimal
from .models import Exam, Subject, ExamSchedule, Mark
from .forms import ExamForm, SubjectForm, ExamScheduleForm, MarkForm
from students.models import Student


def exam_list(request):
    """List exams with statistics and filters"""
    query = request.GET.get('q', '').strip()
    exam_type = request.GET.get('type', '').strip()

    exams = Exam.objects.all()

    if query:
        exams = exams.filter(Q(name__icontains=query) | Q(academic_year__icontains=query) | Q(term__icontains=query))
    if exam_type:
        exams = exams.filter(exam_type=exam_type)

    total_exams = Exam.objects.count()
    total_subjects = Subject.objects.count()
    total_marks_entered = Mark.objects.count()

    context = {
        'page_title': 'Examinations',
        'active_tab': 'exams',
        'exams': exams,
        'query': query,
        'type_filter': exam_type,
        'total_exams': total_exams,
        'total_subjects': total_subjects,
        'total_marks_entered': total_marks_entered,
        'exam_types': Exam.EXAM_TYPE_CHOICES,
    }
    return render(request, 'exams/exam_list.html', context)


def exam_add(request):
    """Add a new exam"""
    if request.method == 'POST':
        form = ExamForm(request.POST)
        if form.is_valid():
            exam = form.save()
            messages.success(request, f'Exam "{exam.name}" created successfully!')
            return redirect('exams:exam_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ExamForm()

    return render(request, 'exams/exam_form.html', {
        'form': form,
        'page_title': 'Create Examination',
        'active_tab': 'exams',
        'action': 'Add',
    })


def exam_edit(request, pk):
    """Edit an existing exam"""
    exam = get_object_or_404(Exam, pk=pk)
    if request.method == 'POST':
        form = ExamForm(request.POST, instance=exam)
        if form.is_valid():
            exam = form.save()
            messages.success(request, f'Exam "{exam.name}" updated successfully!')
            return redirect('exams:exam_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ExamForm(instance=exam)

    return render(request, 'exams/exam_form.html', {
        'form': form,
        'exam': exam,
        'page_title': f'Edit {exam.name}',
        'active_tab': 'exams',
        'action': 'Edit',
    })


def exam_delete(request, pk):
    """Delete an exam"""
    exam = get_object_or_404(Exam, pk=pk)
    if request.method == 'POST':
        name = exam.name
        exam.delete()
        messages.success(request, f'Exam "{name}" was successfully deleted.')
        return redirect('exams:exam_list')

    return render(request, 'exams/exam_confirm_delete.html', {
        'exam': exam,
        'page_title': 'Delete Exam',
        'active_tab': 'exams',
    })


def subject_list(request):
    """List all subjects with assigned teachers"""
    query = request.GET.get('q', '').strip()
    subjects = Subject.objects.select_related('teacher').all()

    if query:
        subjects = subjects.filter(Q(name__icontains=query) | Q(code__icontains=query) | Q(class_grade__icontains=query))

    context = {
        'page_title': 'Subjects & Curriculum',
        'active_tab': 'subjects',
        'subjects': subjects,
        'query': query,
        'total_subjects': subjects.count(),
    }
    return render(request, 'exams/subject_list.html', context)


def subject_add(request):
    """Add a new subject"""
    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            subject = form.save()
            messages.success(request, f'Subject "{subject.name} ({subject.code})" added successfully!')
            return redirect('exams:subject_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SubjectForm()

    return render(request, 'exams/subject_form.html', {
        'form': form,
        'page_title': 'Add Subject',
        'active_tab': 'subjects',
        'action': 'Add',
    })


def subject_edit(request, pk):
    """Edit subject"""
    subject = get_object_or_404(Subject, pk=pk)
    if request.method == 'POST':
        form = SubjectForm(request.POST, instance=subject)
        if form.is_valid():
            subject = form.save()
            messages.success(request, f'Subject "{subject.name}" updated successfully!')
            return redirect('exams:subject_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SubjectForm(instance=subject)

    return render(request, 'exams/subject_form.html', {
        'form': form,
        'subject': subject,
        'page_title': f'Edit {subject.name}',
        'active_tab': 'subjects',
        'action': 'Edit',
    })


def subject_delete(request, pk):
    """Delete subject"""
    subject = get_object_or_404(Subject, pk=pk)
    if request.method == 'POST':
        name = subject.name
        subject.delete()
        messages.success(request, f'Subject "{name}" deleted successfully.')
        return redirect('exams:subject_list')

    return render(request, 'exams/subject_confirm_delete.html', {
        'subject': subject,
        'page_title': 'Delete Subject',
        'active_tab': 'subjects',
    })


def marks_list(request):
    """List exam marks with filters"""
    exam_id = request.GET.get('exam', '')
    subject_id = request.GET.get('subject', '')
    class_filter = request.GET.get('class', '').strip()
    query = request.GET.get('q', '').strip()

    marks = Mark.objects.select_related('exam', 'student', 'subject').all()

    if exam_id:
        marks = marks.filter(exam_id=exam_id)
    if subject_id:
        marks = marks.filter(subject_id=subject_id)
    if class_filter:
        marks = marks.filter(student__student_class=class_filter)
    if query:
        marks = marks.filter(Q(student__student_name__icontains=query) | Q(student__admission_number__icontains=query))

    exams = Exam.objects.all().order_by('-start_date')
    subjects = Subject.objects.all().order_by('name')
    classes = Student.objects.values_list('student_class', flat=True).distinct().order_by('student_class')

    # Quick metrics
    total_marks_count = marks.count()
    pass_count = sum(1 for m in marks if m.is_passed)
    pass_rate = round((pass_count / total_marks_count * 100), 1) if total_marks_count > 0 else 0

    context = {
        'page_title': 'Exam Marks & Grades',
        'active_tab': 'marks',
        'marks': marks,
        'exams': exams,
        'subjects': subjects,
        'classes': classes,
        'selected_exam': exam_id,
        'selected_subject': subject_id,
        'selected_class': class_filter,
        'query': query,
        'total_marks_count': total_marks_count,
        'pass_rate': pass_rate,
        'pass_count': pass_count,
    }
    return render(request, 'exams/marks_list.html', context)


def mark_add(request):
    """Add individual mark record"""
    if request.method == 'POST':
        form = MarkForm(request.POST)
        if form.is_valid():
            try:
                mark = form.save()
                messages.success(request, f'Marks for {mark.student.student_name} ({mark.subject.name}) recorded successfully!')
                return redirect('exams:marks_list')
            except Exception as e:
                messages.error(request, f'Record could not be saved: {e}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = MarkForm()

    return render(request, 'exams/mark_form.html', {
        'form': form,
        'page_title': 'Add Student Mark',
        'active_tab': 'marks',
        'action': 'Add',
    })


def mark_edit(request, pk):
    """Edit individual mark record"""
    mark = get_object_or_404(Mark, pk=pk)
    if request.method == 'POST':
        form = MarkForm(request.POST, instance=mark)
        if form.is_valid():
            mark = form.save()
            messages.success(request, f'Marks for {mark.student.student_name} updated successfully!')
            return redirect('exams:marks_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = MarkForm(instance=mark)

    return render(request, 'exams/mark_form.html', {
        'form': form,
        'mark': mark,
        'page_title': 'Edit Student Mark',
        'active_tab': 'marks',
        'action': 'Edit',
    })


def mark_delete(request, pk):
    """Delete mark record"""
    mark = get_object_or_404(Mark, pk=pk)
    if request.method == 'POST':
        student_name = mark.student.student_name
        subj = mark.subject.name
        mark.delete()
        messages.success(request, f'Mark entry for {student_name} in {subj} deleted.')
        return redirect('exams:marks_list')

    return render(request, 'exams/mark_confirm_delete.html', {
        'mark': mark,
        'page_title': 'Delete Mark Entry',
        'active_tab': 'marks',
    })


def bulk_marks_entry(request):
    """Enter marks in bulk for all students in a class for an exam & subject"""
    exams = Exam.objects.all().order_by('-start_date')
    subjects = Subject.objects.all().order_by('name')
    classes = Student.objects.values_list('student_class', flat=True).distinct().order_by('student_class')

    selected_exam_id = request.GET.get('exam', '')
    selected_subject_id = request.GET.get('subject', '')
    selected_class = request.GET.get('student_class', '')

    students = []
    existing_marks = {}

    if selected_exam_id and selected_subject_id and selected_class:
        students = Student.objects.filter(student_class=selected_class).order_by('student_name')
        marks_qs = Mark.objects.filter(exam_id=selected_exam_id, subject_id=selected_subject_id, student__in=students)
        for m in marks_qs:
            existing_marks[m.student_id] = m

    if request.method == 'POST':
        exam_id = request.POST.get('exam_id')
        subject_id = request.POST.get('subject_id')
        cls = request.POST.get('student_class')
        total_m = Decimal(request.POST.get('total_marks', '100'))

        if not exam_id or not subject_id or not cls:
            messages.error(request, 'Missing exam, subject, or class selection.')
            return redirect('exams:bulk_marks_entry')

        exam = get_object_or_404(Exam, pk=exam_id)
        subject = get_object_or_404(Subject, pk=subject_id)
        class_students = Student.objects.filter(student_class=cls)

        saved_count = 0
        for s in class_students:
            field_name = f'marks_{s.id}'
            remark_field = f'remarks_{s.id}'
            val = request.POST.get(field_name, '').strip()
            rmk = request.POST.get(remark_field, '').strip()

            if val != '':
                try:
                    obtained = Decimal(val)
                    if 0 <= obtained <= total_m:
                        mark_obj, created = Mark.objects.get_or_create(
                            exam=exam,
                            student=s,
                            subject=subject,
                            defaults={'marks_obtained': obtained, 'total_marks': total_m, 'remarks': rmk}
                        )
                        if not created:
                            mark_obj.marks_obtained = obtained
                            mark_obj.total_marks = total_m
                            mark_obj.remarks = rmk
                            mark_obj.save()
                        saved_count += 1
                except Exception:
                    pass

        messages.success(request, f'Successfully recorded/updated marks for {saved_count} students!')
        return redirect(f'/exams/marks/?exam={exam_id}&subject={subject_id}&class={cls}')

    student_rows = []
    for s in students:
        mark_record = existing_marks.get(s.id)
        student_rows.append({
            'student': s,
            'marks_obtained': mark_record.marks_obtained if mark_record else '',
            'remarks': mark_record.remarks if mark_record else '',
            'grade': mark_record.grade if mark_record else '',
        })

    context = {
        'page_title': 'Bulk Marks Entry',
        'active_tab': 'marks_bulk',
        'exams': exams,
        'subjects': subjects,
        'classes': classes,
        'selected_exam_id': selected_exam_id,
        'selected_subject_id': selected_subject_id,
        'selected_class': selected_class,
        'student_rows': student_rows,
        'total_marks_default': 100,
    }
    return render(request, 'exams/bulk_marks_entry.html', context)


def student_report_card(request, student_id):
    """Generate comprehensive student report card / academic transcript"""
    student = get_object_or_404(Student, pk=student_id)
    exam_id = request.GET.get('exam', '')

    marks_qs = Mark.objects.filter(student=student).select_related('exam', 'subject')
    if exam_id:
        marks_qs = marks_qs.filter(exam_id=exam_id)

    exams = Exam.objects.filter(marks__student=student).distinct().order_by('-start_date')

    total_obtained = sum(m.marks_obtained for m in marks_qs)
    total_max = sum(m.total_marks for m in marks_qs)
    overall_percentage = round((float(total_obtained) / float(total_max) * 100), 1) if total_max > 0 else 0

    if overall_percentage >= 90:
        overall_grade = "A+"
        grade_badge_class = "badge-success"
    elif overall_percentage >= 80:
        overall_grade = "A"
        grade_badge_class = "badge-success"
    elif overall_percentage >= 70:
        overall_grade = "B"
        grade_badge_class = "badge-primary"
    elif overall_percentage >= 60:
        overall_grade = "C"
        grade_badge_class = "badge-warning"
    elif overall_percentage >= 50:
        overall_grade = "D"
        grade_badge_class = "badge-warning"
    elif overall_percentage >= 40:
        overall_grade = "E"
        grade_badge_class = "badge-danger"
    else:
        overall_grade = "F"
        grade_badge_class = "badge-danger"

    passed_all = all(m.is_passed for m in marks_qs) if marks_qs else False

    context = {
        'page_title': f'Report Card — {student.student_name}',
        'active_tab': 'students',
        'student': student,
        'marks': marks_qs,
        'exams': exams,
        'selected_exam_id': exam_id,
        'total_obtained': total_obtained,
        'total_max': total_max,
        'overall_percentage': overall_percentage,
        'overall_grade': overall_grade,
        'grade_badge_class': grade_badge_class,
        'passed_all': passed_all,
    }
    return render(request, 'exams/student_report_card.html', context)
