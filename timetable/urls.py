from django.urls import path
from . import views

app_name = 'timetable'

urlpatterns = [
    # Weekly matrix & routines
    path('', views.class_timetable_view, name='class_timetable'),
    path('teacher/', views.teacher_timetable_view, name='teacher_timetable'),
    path('teacher/<int:teacher_id>/', views.teacher_timetable_view, name='teacher_timetable_detail'),

    # Timetable entries CRUD
    path('entry/add/', views.entry_add, name='entry_add'),
    path('entry/<int:pk>/edit/', views.entry_edit, name='entry_edit'),
    path('entry/<int:pk>/delete/', views.entry_delete, name='entry_delete'),

    # Bell Schedule Periods CRUD
    path('periods/', views.period_list, name='period_list'),
    path('periods/add/', views.period_add, name='period_add'),
    path('periods/<int:pk>/edit/', views.period_edit, name='period_edit'),
    path('periods/<int:pk>/delete/', views.period_delete, name='period_delete'),
]
