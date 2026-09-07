import json
import traceback
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Center, Project
import jwt
from django.conf import settings
from core_system.tenants.models import Tenant
def parse_body(request):
    if not request.body:
        return {}
    try:
        return json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        raise ValueError("صيغة بيانات غير صالحة")

from django.db import IntegrityError

def is_tenant_admin(request):
    """دالة مساعدة للتحقق من صلاحيات الإدمن من خلال توكن JWT"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return False
    token = auth_header.split(' ')[1]
    try:
        jwt_secret = getattr(settings, 'JWT_SECRET_KEY', settings.SECRET_KEY)
        payload = jwt.decode(token, jwt_secret, algorithms=["HS256"])
        return payload.get('role') == 'TENANT_ADMIN'
    except Exception:
        return False


def get_tenant_db(request):
    """استخراج اسم قاعدة بيانات المسجد وتجهيز الاتصال بها ديناميكياً"""
    tenant_id = request.headers.get('Tenant-ID')
    if not tenant_id:
        raise ValueError("ترويسة Tenant-ID مفقودة في الطلب")
    
    tenant = Tenant.objects.using('default').get(id=tenant_id)
    db_name = tenant.db_name
    
    if db_name not in settings.DATABASES:
        new_db_config = settings.DATABASES['default'].copy()
        new_db_config.update({
            'NAME': tenant.db_name,
            'USER': tenant.db_user,
            'PASSWORD': tenant.db_password_hash,
            'HOST': tenant.db_host,
            'PORT': tenant.db_port,
        })
        settings.DATABASES[db_name] = new_db_config
        
    return db_name

@csrf_exempt
def center_list_create_view(request):
    try:
        db_name = get_tenant_db(request)
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)

    if request.method == 'GET':
        try:
            # توجيه القراءة للقاعدة الصحيحة
            centers = Center.objects.using(db_name).all().order_by('-created_at')
            res = [{"id": str(c.id), "name": c.name, "code": c.code, "address": c.address} for c in centers]
            return JsonResponse({"status": "success", "count": len(res), "data": res}, status=200)
        except Exception as e:
            return JsonResponse({"status": "error", "message": "حدث خطأ عند استرجاع المراكز", "details": str(e)}, status=500)

    elif request.method == 'POST':
        if not is_tenant_admin(request):
            return JsonResponse({"status": "error", "message": "صلاحيات مدير النظام مطلوبة لإنشاء مركز جديد"}, status=403)
        try:
            data = parse_body(request)
            if not data.get('name') or not data.get('code'):
                return JsonResponse({"status": "error", "message": "الاسم والكود مطلوبان"}, status=400)

            # توجيه الحفظ للقاعدة الصحيحة
            center = Center.objects.using(db_name).create(
                name=data['name'],
                code=data['code'],
                address=data.get('address')
            )
            return JsonResponse({
                "status": "success",
                "message": "تم إضافة المركز بنجاح",
                "data": {"id": str(center.id), "name": center.name, "code": center.code}
            }, status=201)
        except Exception as e:
            return JsonResponse({"status": "error", "message": "فشل إنشاء المركز", "details": str(e)}, status=500)
    else:
        return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)


@csrf_exempt
def center_detail_view(request, pk):
    # 1. استخراج قاعدة بيانات المسجد ديناميكياً
    try:
        db_name = get_tenant_db(request)
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)

    # 2. توجيه الاستعلام للقاعدة الصحيحة
    try:
        center = Center.objects.using(db_name).get(id=pk)
    except Center.DoesNotExist:
        return JsonResponse({"status": "error", "message": "المركز المطلوب غير موجود"}, status=404)

    # التحقق من صلاحيات الإدمن للتعديل أو الإيقاف
    if not is_tenant_admin(request):
        return JsonResponse({"status": "error", "message": "عذراً، صلاحيات الإدمن مطلوبة لإجراء هذا التعديل"}, status=403)

    # حماية المركز الرئيسي الافتراضي
    if center.code == 'MAIN_CENTER':
        return JsonResponse({
            "status": "error", 
            "message": "لا يمكن تعديل أو إلغاء تنشيط المركز الرئيسي لأنه المركز الافتراضي للنظام"
        }, status=403)

    if request.method == 'PUT':
        try:
            data = parse_body(request)
            center.name = data.get('name', center.name)
            center.code = data.get('code', center.code)
            center.address = data.get('address', center.address)
            center.latitude = data.get('latitude', center.latitude)
            center.longitude = data.get('longitude', center.longitude)
            
            if data.get('manager_id'):
                from django.contrib.auth import get_user_model
                User = get_user_model()
                # توجيه البحث عن المستخدم أيضاً لقاعدة المسجد
                center.manager = User.objects.using(db_name).get(id=data['manager_id'])

            # 3. حفظ التعديلات في قاعدة المسجد الصحيحة
            center.save(using=db_name)
            return JsonResponse({"status": "success", "message": "تم تعديل بيانات المركز بنجاح"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": "فشل تعديل المركز", "details": str(e)}, status=500)

    elif request.method == 'PATCH':
        try:
            data = parse_body(request)
            if 'is_active' in data:
                center.is_active = data['is_active']
                # حفظ التعديلات في قاعدة المسجد الصحيحة
                center.save(using=db_name)
                state = "تنشيط" if center.is_active else "إلغاء تنشيط"
                return JsonResponse({"status": "success", "message": f"تم {state} المركز بنجاح"})
            return JsonResponse({"status": "error", "message": "يجب تمرير حالة is_active"}, status=400)
        except Exception as e:
            return JsonResponse({"status": "error", "message": "فشل تغيير حالة المركز", "details": str(e)}, status=500)

    return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)

@csrf_exempt
def project_list_create_view(request):
    print("\n==========================================")
    print(f"[START] Projects API (tenant_modules.centers_and_projects): Method={request.method}")
    print("==========================================")
    
    if request.method == 'GET':
        try:
            print("  [STEP 1] Fetching Projects...")
            projects = Project.objects.select_related('center').all().order_by('-created_at')
            print(f"  [STEP 2] Found {projects.count()} project(s).")
            
            res = []
            for p in projects:
                res.append({
                    "id": str(p.id),
                    "center_id": str(p.center.id),
                    "center_name": p.center.name,
                    "title": p.title,
                    "description": p.description,
                    "created_at": p.created_at.isoformat()
                })
            print(f"[RESULT] Successfully fetched {len(res)} projects.")
            return JsonResponse({"status": "success", "count": len(res), "data": res}, status=200)
        except Exception as e:
            print(f"[ERROR] Failed to query projects: {str(e)}")
            print(traceback.format_exc())
            return JsonResponse({"status": "error", "message": "خطأ عند استرجاع المشاريع", "details": str(e)}, status=500)

    elif request.method == 'POST':
        try:
            print("  [STEP 1] Parsing payload for new Center...")
            data = parse_body(request)
            
            if not data.get('name') or not data.get('code'):
                return JsonResponse({"status": "error", "message": "الاسم والكود مطلوبان"}, status=400)

            manager = None
            if data.get('manager_id'):
                from django.contrib.auth import get_user_model
                User = get_user_model()
                try:
                    manager = User.objects.get(id=data['manager_id'])
                except User.DoesNotExist:
                    return JsonResponse({"status": "error", "message": "حساب المدير المحدد غير موجود"}, status=404)

            print("  [STEP 2] Saving Center to DB...")
            center = Center.objects.create(
                name=data['name'],
                code=data['code'],
                address=data.get('address'),
                manager=manager
            )
            print(f"  [STEP 3] Center saved with ID={center.id}")
            return JsonResponse({
                "status": "success",
                "message": "تم إضافة المركز بنجاح",
                "data": {
                    "id": str(center.id), 
                    "name": center.name, 
                    "code": center.code,
                    "manager_id": str(manager.id) if manager else None
                }
            }, status=201)
        except Center.DoesNotExist:
            return JsonResponse({"status": "error", "message": "المركز المرتبط غير موجود"}, status=404)
        except Exception as e:
            print(f"[ERROR] Project creation failed: {str(e)}")
            print(traceback.format_exc())
            return JsonResponse({"status": "error", "message": "حدث خطأ عند حفظ المشروع", "details": str(e)}, status=500)
    else:
        return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)
