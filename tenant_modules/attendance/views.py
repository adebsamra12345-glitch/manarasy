import json
import uuid
import traceback
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError
from .models import AttendanceLog

def parse_body(request):
    if not request.body:
        return {}
    try:
        return json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        raise ValueError("بيانات غير صالحة")

@csrf_exempt
def attendance_list_create_view(request):
    print("\n==========================================")
    print(f"[START] Attendance API (tenant_modules.attendance): Method={request.method}")
    print("==========================================")
    
    if request.method == 'GET':
        try:
            print("  [STEP 1] Fetching Attendance Logs...")
            logs = AttendanceLog.objects.all().order_by('-session_date')
            print(f"  [STEP 2] Found {logs.count()} record(s).")
            
            res = []
            for log in logs:
                res.append({
                    "id": str(log.id),
                    "student_id": str(log.student_id),
                    "halaqa_id": str(log.halaqa_id),
                    "teacher_id": str(log.teacher_id),
                    "session_date": log.session_date.isoformat(),
                    "status": log.status,
                    "check_in_time": log.check_in_time.isoformat() if log.check_in_time else None,
                    "notes": log.notes
                })
            print(f"[RESULT] Successfully fetched {len(res)} attendance logs.")
            return JsonResponse({"status": "success", "count": len(res), "data": res}, status=200)

        except Exception as e:
            print(f"[ERROR] Failed to fetch attendance: {str(e)}")
            print(traceback.format_exc())
            return JsonResponse({"status": "error", "message": "حدث خطأ عند استرجاع سجل الحضور", "details": str(e)}, status=500)

    elif request.method == 'POST':
        try:
            print("  [STEP 1] Parsing payload for Attendance...")
            data = parse_body(request)
            
            req = ['student_id', 'halaqa_id', 'teacher_id', 'status']
            for r in req:
                if not data.get(r):
                    return JsonResponse({"status": "error", "message": f"الحقل {r} مطلوب"}, status=400)

            student_id = uuid.UUID(str(data['student_id']))
            halaqa_id = uuid.UUID(str(data['halaqa_id']))
            teacher_id = uuid.UUID(str(data['teacher_id']))

            print("  [STEP 2] Saving Attendance record into DB...")
            att = AttendanceLog.objects.create(
                student_id=student_id,
                halaqa_id=halaqa_id,
                teacher_id=teacher_id,
                status=data['status'],
                check_in_time=data.get('check_in_time'),
                notes=data.get('notes')
            )
            print(f"  [STEP 3] Attendance logged successfully with ID={att.id}")
            return JsonResponse({
                "status": "success",
                "message": "تم تسجيل الحضور والغياب بنجاح",
                "data": {
                    "id": str(att.id),
                    "student_id": str(att.student_id),
                    "session_date": att.session_date.isoformat(),
                    "status": att.status
                }
            }, status=201)

        except IntegrityError as e:
            print(f"[ERROR] Duplicate attendance constraint: {str(e)}")
            return JsonResponse({"status": "error", "message": "تم تسجيل حضور الطالب لهذا اليوم مسبقاً", "details": str(e)}, status=400)

        except ValueError as e:
            print(f"[ERROR] Invalid UUID format: {str(e)}")
            return JsonResponse({"status": "error", "message": "صيغة المعرفات (UUID) غير صحيحة", "details": str(e)}, status=400)

        except Exception as e:
            print(f"[ERROR] Attendance registration failed: {str(e)}")
            print(traceback.format_exc())
            return JsonResponse({"status": "error", "message": "حدث خطأ أثناء تسجيل الحضور", "details": str(e)}, status=500)
    else:
        return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)
