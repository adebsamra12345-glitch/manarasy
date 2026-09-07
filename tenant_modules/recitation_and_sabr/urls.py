from django.urls import path
from .views import recitation_list_create_view

urlpatterns = [
    path('', recitation_list_create_view, name='recitation_list_create'),
]
