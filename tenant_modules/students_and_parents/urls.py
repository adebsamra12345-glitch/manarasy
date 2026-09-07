from django.urls import path
from .views import student_list_create_view, parent_list_create_view

urlpatterns = [
    path('students/', student_list_create_view, name='student_list_create'),
    path('parents/', parent_list_create_view, name='parent_list_create'),
]
