import uuid
from django.db import models
from tenant_modules.attendance.models import AttendanceLog

class RecitationLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # علاقة 1:1 مع الحضور: لا تسميع بدون حضور مسبق
    attendance = models.OneToOneField(AttendanceLog, on_delete=models.CASCADE)
    student_id = models.UUIDField()
    recitation_type = models.CharField(max_length=30, choices=[
        ('NEW_MEMORIZATION', 'حفظ جديد'), 
        ('MINOR_REVIEW', 'مراجعة صغرى'), 
        ('MAJOR_REVIEW', 'مراجعة كبرى')
    ])
    from_surah = models.IntegerField()
    from_ayah = models.IntegerField()
    to_surah = models.IntegerField()
    to_ayah = models.IntegerField()
    grade = models.CharField(max_length=20)
    memorization_mistakes_count = models.IntegerField(default=0)
    tajweed_mistakes_count = models.IntegerField(default=0)
    audio_note_s3_url = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = 'recitation_logs'