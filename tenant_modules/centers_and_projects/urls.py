from django.urls import path
from .views import center_list_create_view, project_list_create_view, center_detail_view

urlpatterns = [
    path('centers/', center_list_create_view, name='center_list_create'),
    path('centers/<uuid:pk>/', center_detail_view, name='center_detail'),
    path('projects/', project_list_create_view, name='project_list_create'),
]