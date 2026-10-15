from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    # Core HTML Pages (Practical Work 1)
    path('', views.dashboard_view, name='dashboard'),
    path('students/', views.student_list_view, name='student_list'),
    path('students/add/', views.student_create_view, name='student_add'),
    path('students/<int:id>/edit/', views.student_update_view, name='student_edit'),
    path('students/<int:id>/delete/', views.student_delete_view, name='student_delete'),

    # REST API Endpoints (DRF Compliant with API Specification Sec. 6)
    path('api/students/', views.api_student_list_create, name='api_student_list_create'),
    path('api/students/<int:id>/', views.api_student_detail_update_delete, name='api_student_detail'),
    path('api/dashboard/stats/', views.api_dashboard_stats, name='api_dashboard_stats'),
]

