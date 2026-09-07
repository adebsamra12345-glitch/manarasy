from django.urls import path
from .views import attendance_list_create_view

urlpatterns = [
    path('', attendance_list_create_view, name='attendance_list_create'),
]
