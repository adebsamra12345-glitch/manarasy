import uuid
from django.db import models

class AttendanceLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student_id = models.UUIDField() # سيتم ربطه بـ Student Model
    halaqa_id = models.UUIDField()  # سيتم ربطه بـ Halaqa Model
    teacher_id = models.UUIDField()
    session_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('PRESENT', 'Present'), ('ABSENT', 'Absent'), 
        ('EXCUSED', 'Excused'), ('LATE', 'Late')
    ])
    check_in_time = models.TimeField(null=True, blank=True)
    notes = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'attendance_logs'
        unique_together = ('student_id', 'session_date')