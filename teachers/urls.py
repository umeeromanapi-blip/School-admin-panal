from django.urls import path
from . import views
from . import api_views

app_name = 'teachers'

urlpatterns = [
    path('', views.teacher_list_view, name='teacher_list'),
    path('add/', views.teacher_create_view, name='teacher_add'),
    path('<int:id>/edit/', views.teacher_update_view, name='teacher_edit'),
    path('<int:id>/delete/', views.teacher_delete_view, name='teacher_delete'),
    path('<int:id>/profile/', views.teacher_detail_view, name='teacher_detail'),

    # REST API endpoints
    path('api/', api_views.api_teacher_list_create, name='api_teacher_list_create'),
    path('api/<int:id>/', api_views.api_teacher_detail_update_delete, name='api_teacher_detail'),
]

