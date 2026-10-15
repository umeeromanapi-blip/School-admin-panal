from django.urls import path
from . import views
from . import api_views

app_name = 'announcements'

urlpatterns = [
    path('', views.announcement_list, name='announcement_list'),
    path('add/', views.announcement_add, name='announcement_add'),
    path('<int:pk>/', views.announcement_detail, name='announcement_detail'),
    path('<int:pk>/edit/', views.announcement_edit, name='announcement_edit'),
    path('<int:pk>/delete/', views.announcement_delete, name='announcement_delete'),

    # REST API endpoints
    path('api/', api_views.api_announcement_list_create, name='api_announcement_list_create'),
    path('api/<int:id>/', api_views.api_announcement_detail_update_delete, name='api_announcement_detail'),
]

