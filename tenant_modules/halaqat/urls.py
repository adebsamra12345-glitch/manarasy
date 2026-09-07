from django.urls import path
from .views import halaqa_list_create_view

urlpatterns = [
    path('', halaqa_list_create_view, name='halaqa_list_create'),
]
