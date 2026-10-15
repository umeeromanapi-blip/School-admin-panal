from django.urls import path
from . import views
from . import api_views

app_name = 'fees'

urlpatterns = [
    path('', views.fee_list_view, name='fee_list'),
    path('add/', views.fee_create_view, name='fee_add'),
    path('<int:id>/edit/', views.fee_update_view, name='fee_edit'),
    path('<int:id>/delete/', views.fee_delete_view, name='fee_delete'),

    # REST API endpoints
    path('api/', api_views.api_fee_list_create, name='api_fee_list_create'),
    path('api/<int:id>/', api_views.api_fee_detail_update_delete, name='api_fee_detail'),
]

