from django.urls import path
from . import views
from . import api_views

app_name = 'attendance'

urlpatterns = [
    path('', views.attendance_list_view, name='attendance_list'),
    path('mark/', views.attendance_mark_view, name='attendance_mark'),
    path('<int:id>/edit/', views.attendance_edit_view, name='attendance_edit'),
    path('<int:id>/delete/', views.attendance_delete_view, name='attendance_delete'),
    path('student/<int:student_id>/report/', views.attendance_student_report_view, name='attendance_student_report'),

    # REST API endpoints
    path('api/', api_views.api_attendance_list_create, name='api_attendance_list_create'),
    path('api/<int:id>/', api_views.api_attendance_detail_update_delete, name='api_attendance_detail'),
]

