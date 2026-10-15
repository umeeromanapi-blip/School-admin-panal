from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from .models import Teacher
from .forms import TeacherForm


def teacher_list_view(request):
    query = request.GET.get('q', '').strip()
    dept_filter = request.GET.get('dept', '').strip()
    status_filter = request.GET.get('status', '').strip()

    teachers = Teacher.objects.all().order_by('-created_at')

    if query:
        teachers = teachers.filter(
            Q(full_name__icontains=query) |
            Q(employee_id__icontains=query) |
            Q(subject__icontains=query)
        )
    if dept_filter:
        teachers = teachers.filter(department=dept_filter)
    if status_filter:
        teachers = teachers.filter(status=status_filter)

    total = teachers.count()
    paginator = Paginator(teachers, 10)
    page_obj = paginator.get_page(request.GET.get('page', 1))

    all_depts = Teacher.DEPARTMENT_CHOICES
    all_statuses = Teacher.STATUS_CHOICES

    context = {
        'page_title': 'Teacher Directory',
        'active_tab': 'teachers',
        'page_obj': page_obj,
        'query': query,
        'dept_filter': dept_filter,
        'status_filter': status_filter,
        'total': total,
        'all_depts': all_depts,
        'all_statuses': all_statuses,
    }
    return render(request, 'teachers/teacher_list.html', context)


def teacher_create_view(request):
    if request.method == 'POST':
        form = TeacherForm(request.POST)
        if form.is_valid():
            teacher = form.save()
            messages.success(request, f"Teacher '{teacher.full_name}' ({teacher.employee_id}) added successfully!")
            return redirect('teachers:teacher_list')
        messages.error(request, "Please correct the errors below.")
    else:
        form = TeacherForm()

    context = {
        'page_title': 'Add New Teacher',
        'active_tab': 'teachers',
        'form': form,
        'action_mode': 'create',
    }
    return render(request, 'teachers/teacher_form.html', context)


def teacher_update_view(request, id):
    teacher = get_object_or_404(Teacher, id=id)
    if request.method == 'POST':
        form = TeacherForm(request.POST, instance=teacher)
        if form.is_valid():
            teacher = form.save()
            messages.success(request, f"Teacher record for '{teacher.full_name}' updated successfully!")
            return redirect('teachers:teacher_list')
        messages.error(request, "Please fix the errors below.")
    else:
        form = TeacherForm(instance=teacher)

    context = {
        'page_title': f'Edit Teacher — {teacher.full_name}',
        'active_tab': 'teachers',
        'form': form,
        'teacher': teacher,
        'action_mode': 'update',
    }
    return render(request, 'teachers/teacher_form.html', context)


def teacher_delete_view(request, id):
    teacher = get_object_or_404(Teacher, id=id)
    if request.method == 'POST':
        name = teacher.full_name
        emp_id = teacher.employee_id
        teacher.delete()
        messages.success(request, f"Teacher '{name}' ({emp_id}) removed successfully.")
        return redirect('teachers:teacher_list')
    context = {
        'page_title': f'Confirm Delete — {teacher.full_name}',
        'active_tab': 'teachers',
        'teacher': teacher,
    }
    return render(request, 'teachers/teacher_confirm_delete.html', context)


def teacher_detail_view(request, id):
    teacher = get_object_or_404(Teacher, id=id)
    context = {
        'page_title': f'{teacher.full_name} — Profile',
        'active_tab': 'teachers',
        'teacher': teacher,
    }
    return render(request, 'teachers/teacher_detail.html', context)
