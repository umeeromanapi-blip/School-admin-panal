from django.urls import path
from . import views

app_name = 'library'

urlpatterns = [
    # Books Catalog CRUD
    path('', views.book_list, name='book_list'),
    path('books/add/', views.book_add, name='book_add'),
    path('books/<int:pk>/edit/', views.book_edit, name='book_edit'),
    path('books/<int:pk>/delete/', views.book_delete, name='book_delete'),

    # Loans / Issue & Return
    path('issues/', views.book_issue_list, name='book_issue_list'),
    path('issues/new/', views.book_issue_create, name='book_issue_create'),
    path('issues/<int:pk>/return/', views.book_return_action, name='book_return_action'),
    path('issues/<int:pk>/delete/', views.book_issue_delete, name='book_issue_delete'),
]
