from django.urls import path
from . import views

app_name = 'transport'

urlpatterns = [
    # Routes & Fleet Overview
    path('', views.transport_dashboard, name='transport_dashboard'),
    path('routes/add/', views.route_add, name='route_add'),
    path('routes/<int:pk>/edit/', views.route_edit, name='route_edit'),
    path('routes/<int:pk>/delete/', views.route_delete, name='route_delete'),

    # Fleet Vehicles
    path('vehicles/', views.vehicle_list, name='vehicle_list'),
    path('vehicles/add/', views.vehicle_add, name='vehicle_add'),
    path('vehicles/<int:pk>/edit/', views.vehicle_edit, name='vehicle_edit'),
    path('vehicles/<int:pk>/delete/', views.vehicle_delete, name='vehicle_delete'),

    # Student Transport Passes
    path('passes/', views.allocation_list, name='allocation_list'),
    path('passes/new/', views.allocation_add, name='allocation_add'),
    path('passes/<int:pk>/edit/', views.allocation_edit, name='allocation_edit'),
    path('passes/<int:pk>/delete/', views.allocation_delete, name='allocation_delete'),
]
