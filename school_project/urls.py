from django.contrib import admin
from django.urls import path, include
from students.reports_views import reports_overview
from school_project.api_root import api_root
from teachers.api_views import api_teacher_list_create, api_teacher_detail_update_delete
from attendance.api_views import api_attendance_list_create, api_attendance_detail_update_delete
from fees.api_views import api_fee_list_create, api_fee_detail_update_delete
from announcements.api_views import api_announcement_list_create, api_announcement_detail_update_delete
from exams.api_views import api_exam_list_create, api_subject_list_create, api_mark_list_create

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('students.urls')),
    path('teachers/', include('teachers.urls')),
    path('fees/', include('fees.urls')),
    path('attendance/', include('attendance.urls')),
    path('exams/', include('exams.urls')),
    path('announcements/', include('announcements.urls')),
    path('timetable/', include('timetable.urls')),
    path('library/', include('library.urls')),
    path('transport/', include('transport.urls')),
    path('hostel/', include('hostel.urls')),
    path('reports/', reports_overview, name='reports_overview'),

    # Central REST API Endpoints
    path('api/', api_root, name='api_root'),
    path('api/teachers/', api_teacher_list_create, name='api_teachers_central'),
    path('api/teachers/<int:id>/', api_teacher_detail_update_delete, name='api_teachers_central_detail'),
    path('api/attendance/', api_attendance_list_create, name='api_attendance_central'),
    path('api/attendance/<int:id>/', api_attendance_detail_update_delete, name='api_attendance_central_detail'),
    path('api/fees/', api_fee_list_create, name='api_fees_central'),
    path('api/fees/<int:id>/', api_fee_detail_update_delete, name='api_fees_central_detail'),
    path('api/announcements/', api_announcement_list_create, name='api_announcements_central'),
    path('api/announcements/<int:id>/', api_announcement_detail_update_delete, name='api_announcements_central_detail'),
    path('api/exams/', api_exam_list_create, name='api_exams_central'),
    path('api/subjects/', api_subject_list_create, name='api_subjects_central'),
    path('api/marks/', api_mark_list_create, name='api_marks_central'),
]

