import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Count, Q
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Student
from .forms import StudentForm


# ==========================================
# HTML Page Views (Core Practical Work 1)
# ==========================================

def dashboard_view(request):
    """
    Renders modern dashboard with high-level school analytics, total student metrics,
    class distribution, exam metrics, notice board, and recent student admissions.
    """
    total_students = Student.objects.count()
    class_stats = Student.objects.values('student_class').annotate(
        count=Count('id')
    ).order_by('-count')[:6]
    total_classes = Student.objects.values('student_class').distinct().count()
    recent_students = Student.objects.order_by('-created_at')[:6]

    # Epic 3 & 4 metrics
    try:
        from exams.models import Exam, Subject, Mark
        from announcements.models import Announcement
        from library.models import Book, BookIssue
        from timetable.models import TimetableEntry
        total_exams = Exam.objects.count()
        total_subjects = Subject.objects.count()
        total_marks = Mark.objects.count()
        active_notices = Announcement.objects.filter(is_active=True).order_by('-is_pinned', '-published_date')[:3]
        total_books = Book.objects.count()
        total_active_loans = BookIssue.objects.filter(status='Issued').count()
        total_timetable_slots = TimetableEntry.objects.count()

        # Epic 5 metrics
        from transport.models import Route, Vehicle
        from hostel.models import Hostel, RoomAllocation
        total_routes = Route.objects.count()
        total_vehicles = Vehicle.objects.count()
        total_hostels = Hostel.objects.count()
        active_residents = RoomAllocation.objects.filter(status='Active').count()
    except Exception:
        total_exams = 0
        total_subjects = 0
        total_marks = 0
        active_notices = []
        total_books = 0
        total_active_loans = 0
        total_timetable_slots = 0
        total_routes = 0
        total_vehicles = 0
        total_hostels = 0
        active_residents = 0

    context = {
        'page_title': 'Dashboard',
        'active_tab': 'dashboard',
        'total_students': total_students,
        'total_classes': total_classes,
        'recent_students': recent_students,
        'class_stats': class_stats,
        'total_exams': total_exams,
        'total_subjects': total_subjects,
        'total_marks': total_marks,
        'active_notices': active_notices,
        'total_books': total_books,
        'total_active_loans': total_active_loans,
        'total_timetable_slots': total_timetable_slots,
        'total_routes': total_routes,
        'total_vehicles': total_vehicles,
        'total_hostels': total_hostels,
        'active_residents': active_residents,
    }
    return render(request, 'students/dashboard.html', context)


def student_list_view(request):
    """
    Renders searchable, filterable directory table of all enrolled students
    with quick action triggers for edit and delete.
    """
    query = request.GET.get('q', '').strip()
    class_filter = request.GET.get('class', '').strip()
    sort_by = request.GET.get('sort', '-created_at')

    valid_sorts = {
        'name_asc': 'student_name',
        'name_desc': '-student_name',
        'adm_asc': 'admission_number',
        'adm_desc': '-admission_number',
        'class_asc': 'student_class',
        'class_desc': '-student_class',
        'date_asc': 'created_at',
        'date_desc': '-created_at',
    }
    order_field = valid_sorts.get(sort_by, '-created_at')

    students = Student.objects.all().order_by(order_field)

    if query:
        students = students.filter(
            Q(student_name__icontains=query) |
            Q(admission_number__icontains=query) |
            Q(contact_number__icontains=query)
        )

    if class_filter:
        students = students.filter(student_class__iexact=class_filter)

    total_filtered_count = students.count()
    all_classes = Student.objects.values_list('student_class', flat=True).distinct().order_by('student_class')

    # Pagination: 10 students per page
    paginator = Paginator(students, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_title': 'Student Directory',
        'active_tab': 'students',
        'page_obj': page_obj,
        'query': query,
        'class_filter': class_filter,
        'all_classes': all_classes,
        'total_count': total_filtered_count,
        'sort_by': sort_by,
    }
    return render(request, 'students/student_list.html', context)


def student_create_view(request):
    """
    Handles new student enrollment. Validates form data, checks uniqueness,
    persists record, and redirects to student directory with feedback message.
    """
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            student = form.save()
            messages.success(
                request,
                f"Student '{student.student_name}' (ID: {student.admission_number}) registered successfully!"
            )
            return redirect('students:student_list')
        else:
            messages.error(request, "Please review and correct the errors below.")
    else:
        form = StudentForm()

    context = {
        'page_title': 'Add New Student',
        'active_tab': 'add_student',
        'form': form,
        'action_mode': 'create',
    }
    return render(request, 'students/student_form.html', context)


def student_update_view(request, id):
    """
    Handles editing existing student records. Populates form with current values,
    validates changes, and saves updates.
    """
    student = get_object_or_404(Student, id=id)

    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            updated_student = form.save()
            messages.success(
                request,
                f"Student record for '{updated_student.student_name}' was successfully updated!"
            )
            return redirect('students:student_list')
        else:
            messages.error(request, "Please resolve the errors highlighted below.")
    else:
        form = StudentForm(instance=student)

    context = {
        'page_title': f'Edit Student — {student.student_name}',
        'active_tab': 'students',
        'form': form,
        'student': student,
        'action_mode': 'update',
    }
    return render(request, 'students/student_form.html', context)


def student_delete_view(request, id):
    """
    Confirmation and deletion handler.
    GET: Renders confirmation page without deleting anything.
    POST: Permanently removes the student record after administrator confirmation.
    """
    student = get_object_or_404(Student, id=id)

    if request.method == 'POST':
        student_name = student.student_name
        admission_number = student.admission_number
        student.delete()
        messages.success(
            request,
            f"Student record '{student_name}' ({admission_number}) was permanently removed."
        )
        return redirect('students:student_list')

    context = {
        'page_title': f'Confirm Deletion — {student.student_name}',
        'active_tab': 'students',
        'student': student,
    }
    return render(request, 'students/student_confirm_delete.html', context)


# ==========================================
# Django REST Framework API Endpoints
# (Compliant with API Specification Sec. 6)
# ==========================================
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .serializers import StudentSerializer


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def api_student_list_create(request):
    """
    GET /api/students/ -> Return all student records in JSON (supports ?q= and ?class= search).
    POST /api/students/ -> Create a student record from JSON payload using StudentSerializer.
    """
    if request.method == 'GET':
        query = request.query_params.get('q', '').strip()
        class_filter = request.query_params.get('class', '').strip()

        students = Student.objects.all().order_by('id')
        if query:
            students = students.filter(
                Q(student_name__icontains=query) |
                Q(admission_number__icontains=query) |
                Q(contact_number__icontains=query)
            )
        if class_filter:
            students = students.filter(student_class__iexact=class_filter)

        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = StudentSerializer(data=request.data)
        if serializer.is_valid():
            student = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({'errors': serializer.errors, **serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([AllowAny])
def api_student_detail_update_delete(request, id):
    """
    GET /api/students/<id>/ -> Retrieve single student record.
    PUT / PATCH /api/students/<id>/ -> Update student record using StudentSerializer.
    DELETE /api/students/<id>/ -> Delete student record (204 No Content).
    """
    try:
        student = Student.objects.get(id=id)
    except Student.DoesNotExist:
        return Response({'error': 'Student not found', 'detail': 'Student not found.'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = StudentSerializer(student)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method in ['PUT', 'PATCH']:
        partial = (request.method == 'PATCH')
        serializer = StudentSerializer(student, data=request.data, partial=partial)
        if serializer.is_valid():
            updated_student = serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'errors': serializer.errors, **serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        student.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([AllowAny])
def api_dashboard_stats(request):
    """
    GET /api/dashboard/stats/ -> Return real-time summary statistics for dashboard via API.
    """
    total_students = Student.objects.count()
    class_stats = list(Student.objects.values('student_class').annotate(count=Count('id')).order_by('-count')[:6])
    total_classes = Student.objects.values('student_class').distinct().count()
    recent = StudentSerializer(Student.objects.order_by('-created_at')[:6], many=True).data

    return Response({
        'total_students': total_students,
        'total_classes': total_classes,
        'class_stats': class_stats,
        'recent_students': recent,
    }, status=status.HTTP_200_OK)

