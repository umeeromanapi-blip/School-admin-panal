from django.urls import path
from . import views

app_name = 'hostel'

urlpatterns = [
    # Buildings Overview
    path('', views.hostel_overview, name='hostel_overview'),
    path('buildings/add/', views.hostel_add, name='hostel_add'),
    path('buildings/<int:pk>/edit/', views.hostel_edit, name='hostel_edit'),
    path('buildings/<int:pk>/delete/', views.hostel_delete, name='hostel_delete'),

    # Rooms Management
    path('rooms/', views.room_list, name='room_list'),
    path('rooms/add/', views.room_add, name='room_add'),
    path('rooms/<int:pk>/edit/', views.room_edit, name='room_edit'),
    path('rooms/<int:pk>/delete/', views.room_delete, name='room_delete'),

    # Student Check-ins / Allocations
    path('residents/', views.allocation_list, name='allocation_list'),
    path('residents/new/', views.allocation_add, name='allocation_add'),
    path('residents/<int:pk>/edit/', views.allocation_edit, name='allocation_edit'),
    path('residents/<int:pk>/delete/', views.allocation_delete, name='allocation_delete'),
]
