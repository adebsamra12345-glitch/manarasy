import json
import traceback
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from tenant_modules.centers_and_projects.models import Center
from .models import Halaqa

def parse_body(request):
    if not request.body:
        return {}
    try:
        return json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        raise ValueError("بيانات غير صالحة")

@csrf_exempt
def halaqa_list_create_view(request):
    print("\n==========================================")
    print(f"[START] Halaqat API (tenant_modules.halaqat): Method={request.method}")
    print("==========================================")
    
    if request.method == 'GET':
        try:
            print("  [STEP 1] Querying Halaqat...")
            halaqat = Halaqa.objects.all().order_by('-created_at')
            print(f"  [STEP 2] Found {halaqat.count()} halaqa(s).")
            
            res = []
            for h in halaqat:
                res.append({
                    "id": str(h.id),
                    "center_id": str(h.center.id) if h.center else None,
                    "center_name": h.center.name if h.center else None,
                    "name": h.name,
                    "teacher_name": h.teacher_name,
                    "max_students": h.max_students,
                    "created_at": h.created_at.isoformat()
                })
            print(f"[RESULT] Successfully fetched {len(res)} halaqa(s).")
            return JsonResponse({"status": "success", "count": len(res), "data": res}, status=200)

        except Exception as e:
            print(f"[ERROR] Failed to query halaqat: {str(e)}")
            print(traceback.format_exc())
            return JsonResponse({"status": "error", "message": "حدث خطأ أثناء جلب الحلقات", "details": str(e)}, status=500)

    elif request.method == 'POST':
        try:
            print("  [STEP 1] Parsing payload for new Halaqa...")
            data = parse_body(request)
            
            if not data.get('name') or not data.get('teacher_name'):
                return JsonResponse({"status": "error", "message": "اسم الحلقة واسم المعلم مطلوبان"}, status=400)

            center = None
            if data.get('center_id'):
                try:
                    center = Center.objects.get(id=data['center_id'])
                except Center.DoesNotExist:
                    return JsonResponse({"status": "error", "message": "المركز المحدد غير موجود"}, status=404)

            print("  [STEP 2] Creating Halaqa record in DB...")
            halaqa = Halaqa.objects.create(
                name=data['name'],
                teacher_name=data['teacher_name'],
                center=center,
                max_students=data.get('max_students', 20)
            )
            print(f"  [STEP 3] Halaqa created with ID={halaqa.id}")
            return JsonResponse({
                "status": "success",
                "message": "تم إضافة الحلقة القرآنية بنجاح",
                "data": {
                    "id": str(halaqa.id),
                    "name": halaqa.name,
                    "teacher_name": halaqa.teacher_name,
                    "created_at": halaqa.created_at.isoformat()
                }
            }, status=201)

        except Exception as e:
            print(f"[ERROR] Halaqa creation failed: {str(e)}")
            print(traceback.format_exc())
            return JsonResponse({"status": "error", "message": "حدث خطأ عند حفظ الحلقة", "details": str(e)}, status=500)
    else:
        return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)
