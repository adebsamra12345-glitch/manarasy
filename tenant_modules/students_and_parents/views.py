import json
import traceback
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from tenant_modules.halaqat.models import Halaqa
from .models import Student, Parent

def parse_body(request):
    if not request.body:
        return {}
    try:
        return json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        raise ValueError("صيغة بيانات غير صالحة")

@csrf_exempt
def parent_list_create_view(request):
    print("\n==========================================")
    print(f"[START] Parents API (tenant_modules.students_and_parents): Method={request.method}")
    print("==========================================")
    
    if request.method == 'GET':
        try:
            print("  [STEP 1] Querying Parents...")
            parents = Parent.objects.all().order_by('-created_at')
            print(f"  [STEP 2] Found {parents.count()} parent(s).")
            
            res = []
            for p in parents:
                res.append({
                    "id": str(p.id),
                    "full_name": p.full_name,
                    "phone": p.phone,
                    "email": p.email,
                    "created_at": p.created_at.isoformat()
                })
            print(f"[RESULT] Successfully returned {len(res)} parents.")
            return JsonResponse({"status": "success", "count": len(res), "data": res}, status=200)

        except Exception as e:
            print(f"[ERROR] Failed to query parents: {str(e)}")
            print(traceback.format_exc())
            return JsonResponse({"status": "error", "message": "حدث خطأ أثناء جلب قائمة أولياء الأمور", "details": str(e)}, status=500)

    elif request.method == 'POST':
        try:
            print("  [STEP 1] Parsing payload for new Parent...")
            data = parse_body(request)
            
            if not data.get('full_name') or not data.get('phone'):
                return JsonResponse({"status": "error", "message": "الاسم الكامل ورقم الهاتف مطلوبان"}, status=400)

            print("  [STEP 2] Saving Parent record to DB...")
            parent = Parent.objects.create(
                full_name=data['full_name'],
                phone=data['phone'],
                email=data.get('email')
            )
            print(f"  [STEP 3] Parent saved with ID={parent.id}")
            return JsonResponse({
                "status": "success",
                "message": "تم إضافة ولي الأمر بنجاح",
                "data": {"id": str(parent.id), "full_name": parent.full_name, "phone": parent.phone}
            }, status=201)

        except Exception as e:
            print(f"[ERROR] Parent creation failed: {str(e)}")
            print(traceback.format_exc())
            return JsonResponse({"status": "error", "message": "حدث خطأ أثناء إضافة ولي الأمر", "details": str(e)}, status=500)
    else:
        return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)

@csrf_exempt
def student_list_create_view(request):
    print("\n==========================================")
    print(f"[START] Students API (tenant_modules.students_and_parents): Method={request.method}")
    print("==========================================")
    
    if request.method == 'GET':
        try:
            print("  [STEP 1] Querying Students...")
            students = Student.objects.select_related('parent', 'halaqa').all().order_by('-created_at')
            print(f"  [STEP 2] Found {students.count()} student(s).")
            
            res = []
            for s in students:
                res.append({
                    "id": str(s.id),
                    "full_name": s.full_name,
                    "national_id": s.national_id,
                    "birth_date": s.birth_date.isoformat() if s.birth_date else None,
                    "parent_name": s.parent.full_name if s.parent else None,
                    "halaqa_name": s.halaqa.name if s.halaqa else None,
                    "created_at": s.created_at.isoformat()
                })
            print(f"[RESULT] Successfully returned {len(res)} students.")
            return JsonResponse({"status": "success", "count": len(res), "data": res}, status=200)

        except Exception as e:
            print(f"[ERROR] Failed to query students: {str(e)}")
            print(traceback.format_exc())
            return JsonResponse({"status": "error", "message": "حدث خطأ عند استرجاع ملفات الطلاب", "details": str(e)}, status=500)

    elif request.method == 'POST':
        try:
            print("  [STEP 1] Parsing payload for new Student...")
            data = parse_body(request)
            
            if not data.get('full_name'):
                return JsonResponse({"status": "error", "message": "الاسم الكامل للطالب مطلوب"}, status=400)

            parent = None
            if data.get('parent_id'):
                try:
                    parent = Parent.objects.get(id=data['parent_id'])
                except Parent.DoesNotExist:
                    return JsonResponse({"status": "error", "message": "ولي الأمر المرتبط غير موجود"}, status=404)

            halaqa = None
            if data.get('halaqa_id'):
                try:
                    halaqa = Halaqa.objects.get(id=data['halaqa_id'])
                except Halaqa.DoesNotExist:
                    return JsonResponse({"status": "error", "message": "الحلقة القرآنية غير موجودة"}, status=404)

            print("  [STEP 2] Saving Student to DB...")
            student = Student.objects.create(
                full_name=data['full_name'],
                parent=parent,
                halaqa=halaqa,
                national_id=data.get('national_id'),
                birth_date=data.get('birth_date')
            )
            print(f"  [STEP 3] Student created with ID={student.id}")
            return JsonResponse({
                "status": "success",
                "message": "تم إنشاء ملف الطالب بنجاح",
                "data": {"id": str(student.id), "full_name": student.full_name}
            }, status=201)

        except Exception as e:
            print(f"[ERROR] Student creation failed: {str(e)}")
            print(traceback.format_exc())
            return JsonResponse({"status": "error", "message": "حدث خطأ عند إضافة الطالب", "details": str(e)}, status=500)
    else:
        return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)
