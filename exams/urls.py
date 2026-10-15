from django.urls import path
from . import views
from . import api_views

app_name = 'exams'

urlpatterns = [
    # Exams CRUD
    path('', views.exam_list, name='exam_list'),
    path('add/', views.exam_add, name='exam_add'),
    path('<int:pk>/edit/', views.exam_edit, name='exam_edit'),
    path('<int:pk>/delete/', views.exam_delete, name='exam_delete'),

    # Subjects CRUD
    path('subjects/', views.subject_list, name='subject_list'),
    path('subjects/add/', views.subject_add, name='subject_add'),
    path('subjects/<int:pk>/edit/', views.subject_edit, name='subject_edit'),
    path('subjects/<int:pk>/delete/', views.subject_delete, name='subject_delete'),

    # Marks & Grading
    path('marks/', views.marks_list, name='marks_list'),
    path('marks/add/', views.mark_add, name='mark_add'),
    path('marks/<int:pk>/edit/', views.mark_edit, name='mark_edit'),
    path('marks/<int:pk>/delete/', views.mark_delete, name='mark_delete'),
    path('marks/bulk/', views.bulk_marks_entry, name='bulk_marks_entry'),

    # Student Academic Report Card
    path('report-card/<int:student_id>/', views.student_report_card, name='student_report_card'),

    # REST API endpoints
    path('api/exams/', api_views.api_exam_list_create, name='api_exam_list_create'),
    path('api/subjects/', api_views.api_subject_list_create, name='api_subject_list_create'),
    path('api/marks/', api_views.api_mark_list_create, name='api_mark_list_create'),
]

