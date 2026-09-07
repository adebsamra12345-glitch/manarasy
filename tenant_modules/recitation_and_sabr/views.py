import json
import traceback
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError
from tenant_modules.attendance.models import AttendanceLog
from .models import RecitationLog

def parse_body(request):
    if not request.body:
        return {}
    try:
        return json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        raise ValueError("بيانات غير صالحة")

@csrf_exempt
def recitation_list_create_view(request):
    print("\n==========================================")
    print(f"[START] Recitation API (tenant_modules.recitation_and_sabr): Method={request.method}")
    print("==========================================")
    
    if request.method == 'GET':
        try:
            print("  [STEP 1] Querying Recitation logs from DB...")
            logs = RecitationLog.objects.select_related('attendance').all().order_by('-created_at')
            print(f"  [STEP 2] Found {logs.count()} record(s).")
            
            res = []
            for r in logs:
                res.append({
                    "id": str(r.id),
                    "attendance_id": str(r.attendance.id),
                    "student_id": str(r.student_id),
                    "recitation_type": r.recitation_type,
                    "from_surah": r.from_surah,
                    "from_ayah": r.from_ayah,
                    "to_surah": r.to_surah,
                    "to_ayah": r.to_ayah,
                    "grade": r.grade,
                    "memorization_mistakes_count": r.memorization_mistakes_count,
                    "tajweed_mistakes_count": r.tajweed_mistakes_count,
                    "audio_note_s3_url": r.audio_note_s3_url,
                    "created_at": r.created_at.isoformat()
                })
            print(f"[RESULT] Successfully fetched {len(res)} recitation logs.")
            return JsonResponse({"status": "success", "count": len(res), "data": res}, status=200)

        except Exception as e:
            print(f"[ERROR] Recitation query failed: {str(e)}")
            print(traceback.format_exc())
            return JsonResponse({"status": "error", "message": "حدث خطأ أثناء جلب سجل التسميع", "details": str(e)}, status=500)

    elif request.method == 'POST':
        try:
            print("  [STEP 1] Parsing payload for Recitation entry...")
            data = parse_body(request)
            
            req_fields = ['attendance_id', 'recitation_type', 'from_surah', 'from_ayah', 'to_surah', 'to_ayah', 'grade']
            for f in req_fields:
                if f not in data or data[f] is None:
                    return JsonResponse({"status": "error", "message": f"الحقل {f} مطلوب"}, status=400)

            print(f"  [STEP 2] Verifying Attendance Log ID={data['attendance_id']}")
            att = AttendanceLog.objects.get(id=data['attendance_id'])
            
            print("  [STEP 3] Saving Recitation Log...")
            rec = RecitationLog.objects.create(
                attendance=att,
                student_id=att.student_id,
                recitation_type=data['recitation_type'],
                from_surah=int(data['from_surah']),
                from_ayah=int(data['from_ayah']),
                to_surah=int(data['to_surah']),
                to_ayah=int(data['to_ayah']),
                grade=str(data['grade']),
                memorization_mistakes_count=int(data.get('memorization_mistakes_count', 0)),
                tajweed_mistakes_count=int(data.get('tajweed_mistakes_count', 0)),
                audio_note_s3_url=data.get('audio_note_s3_url')
            )
            print(f"  [STEP 4] Recitation logged with ID={rec.id}")
            return JsonResponse({
                "status": "success",
                "message": "تم حفظ التسميع والسبر بنجاح",
                "data": {
                    "id": str(rec.id),
                    "attendance_id": str(att.id),
                    "student_id": str(rec.student_id),
                    "recitation_type": rec.recitation_type,
                    "grade": rec.grade,
                    "created_at": rec.created_at.isoformat()
                }
            }, status=201)

        except AttendanceLog.DoesNotExist:
            print(f"[ERROR] AttendanceLog {data.get('attendance_id')} not found.")
            return JsonResponse({"status": "error", "message": "سجل الحضور المرتبط غير موجود"}, status=404)

        except IntegrityError as e:
            print(f"[ERROR] Integrity error: {str(e)}")
            return JsonResponse({"status": "error", "message": "تم تسجيل التسميع مسبقاً لهذا الحضور", "details": str(e)}, status=400)

        except Exception as e:
            print(f"[ERROR] Recitation recording failed: {str(e)}")
            print(traceback.format_exc())
            return JsonResponse({"status": "error", "message": "حدث خطأ عند حفظ التسميع", "details": str(e)}, status=500)

    else:
        return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)
