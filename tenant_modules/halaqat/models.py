import uuid
from django.db import models
from tenant_modules.centers_and_projects.models import Center

class Halaqa(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    center = models.ForeignKey(Center, on_delete=models.SET_NULL, null=True, blank=True, related_name='halaqat')
    name = models.CharField(max_length=150)
    teacher_name = models.CharField(max_length=150)
    max_students = models.IntegerField(default=20)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'halaqat'
    
