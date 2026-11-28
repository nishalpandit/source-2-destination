"""
API views for student mobile app and kiosk devices.
"""
import os
import json
import uuid
from datetime import timedelta
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db import transaction
from django.db.models import Q, Sum

from .models import (
    School, Student, Guardian, KioskDevice, DeviceAssignment, CallRecord,
    HostelWarden, RechargePlan, StudentRecharge, CallingScheduleRule
)
from .calling_services import (
    CallingDurationEngine, CallingScheduleEngine, CallAuthorizationEngine, CallSessionManager,
    ValidityService, get_global_duration_rule
)


def _parse_request_data(request):
    """Parse request body as JSON or fallback to POST/GET params."""
    if request.body:
        try:
            return json.loads(request.body.decode('utf-8'))
        except (ValueError, UnicodeDecodeError):
            pass
    return request.POST.dict() or request.GET.dict()


def api_status(request):
    """Health check endpoint."""
    return JsonResponse({
        "status": "online",
        "service": "Source 2 Destination Student Mobile & Kiosk API",
        "version": "2.5.0-kiosk",
        "mode": "PLAN_A_DEVICE_BINDING_ACTIVE"
    })
 

@csrf_exempt
def device_enroll(request):
    """Register kiosk hardware or update last seen timestamp."""
    if request.method != "POST":
        return JsonResponse({"error": "METHOD_NOT_ALLOWED", "message": "POST required for device enrollment."}, status=405)

    data = _parse_request_data(request)
    device_id = (data.get('device_id') or '').strip()
    if not device_id:
        return JsonResponse({"error": "MISSING_DEVICE_ID", "message": "Hardware device_id is required."}, status=400)

    school_code = (data.get('school_code') or '').strip()
    school = None
    if school_code:
        school = School.objects.filter(code__iexact=school_code).first()
        if not school:
            return JsonResponse({
                "error": "SCHOOL_NOT_FOUND",
                "message": f"Campus with code '{school_code}' not found. Please verify the school_code assigned to this device."
            }, status=404)
    else:
        # Fall back to single campus ONLY if exactly 1 school exists in the database
        if School.objects.count() == 1:
            school = School.objects.first()
        elif School.objects.count() == 0:
            school, _ = School.objects.get_or_create(
                code='SCH-1001',
                defaults={
                    "name": "Doon Valley Residential Academy",
                    "city": "Dehradun",
                    "admin_name": "Campus Administrator",
                    "admin_email": "admin@doonvalley.edu.in",
                    "status": "Active",
                }
            )
        else:
            return JsonResponse({
                "error": "MISSING_SCHOOL_CODE",
                "message": "Multiple campuses exist on this platform. Please provide 'school_code' in the enrollment payload to bind this device to your specific school."
            }, status=400)

    model_name = (data.get('model_name') or data.get('name') or "Android Kiosk Phone").strip()
    serial_number = (data.get('serial_number') or '').strip()
    imei = (data.get('imei') or '').strip()
    mac_address = (data.get('mac_address') or '').strip()

    device, created = KioskDevice.objects.get_or_create(
        device_id=device_id,
        defaults={
            "school": school,
            "name": model_name,
            "serial_number": serial_number,
            "imei": imei,
            "mac_address": mac_address,
            "kiosk_mode_locked": True,
            "status": "Online",
            "assignment_type": "Student",
            "last_heartbeat": timezone.now(),
        }
    )

    if not created:
        device.school = school
        device.name = model_name
        if serial_number:
            device.serial_number = serial_number
        if imei:
            device.imei = imei
        if mac_address:
            device.mac_address = mac_address
        device.status = "Online"
        device.last_heartbeat = timezone.now()
        device.save(update_fields=['school', 'name', 'serial_number', 'imei', 'mac_address', 'status', 'last_heartbeat'])

    return JsonResponse({
        "status": "success",
        "device_id": device.device_id,
        "name": device.name,
        "device": {
            "device_id": device.device_id,
            "name": device.name,
        }
    }, status=201 if created else 200)


@csrf_exempt
def device_heartbeat(request):
    """Keep-alive ping from kiosk devices."""
    data = _parse_request_data(request)
    device_id = (data.get('device_id') or '').strip()

    if device_id:
        device = KioskDevice.objects.filter(device_id=device_id).first()
        if device:
            device.last_heartbeat = timezone.now()
            device.status = 'Online'
            device.save(update_fields=['last_heartbeat', 'status'])

    return JsonResponse({
        "status": "online"
    })


@csrf_exempt
def student_auth(request):
    """Authenticate student by device and student code, returning limits and contacts."""
    if request.method != "POST":
        return JsonResponse({"error": "METHOD_NOT_ALLOWED", "message": "POST required for student authentication."}, status=405)

    data = _parse_request_data(request)
    device_id = (data.get('device_id') or '').strip()
    student_code = (data.get('student_code') or data.get('code') or '').strip()
    pin = str(data.get('pin') or '').strip()

    if not device_id:
        return JsonResponse({"error": "MISSING_DEVICE_ID", "message": "device_id is required."}, status=400)

    # check if device is registered
    device = KioskDevice.objects.filter(device_id=device_id).select_related('school', 'assigned_student').first()
    if not device:
        return JsonResponse({
            "error": "DEVICE_NOT_ENROLLED",
            "message": "This device is not enrolled in the campus system."
        }, status=404)

    # resolve student if device is assigned to a specific student
    if not student_code and device.assignment_type == 'Student' and device.assigned_student:
        student_code = device.assigned_student.code

    if not student_code:
        return JsonResponse({"error": "MISSING_STUDENT_CODE", "message": "student_code is required."}, status=400)

    # verify device assignment
    if device.assignment_type == 'Student':
        if not device.assigned_student:
            return JsonResponse({
                "error": "DEVICE_NOT_ASSIGNED",
                "message": "This device has not been assigned to a student yet. Contact School Admin."
            }, status=403)

        if device.assigned_student.code != student_code and getattr(device.assigned_student, 'calling_code', None) != student_code:
            return JsonResponse({
                "error": "HARDWARE_MISMATCH",
                "message": f"This device is assigned exclusively to {device.assigned_student.name} ({device.assigned_student.code}). Login rejected."
            }, status=403)

        student = device.assigned_student
    else:
        # shared booth mode - match against school
        student = Student.objects.filter(
            Q(code=student_code) | Q(calling_code=student_code),
            school=device.school
        ).first()
        if not student:
            return JsonResponse({
                "error": "INVALID_STUDENT",
                "message": f"Student code {student_code} does not exist at {device.school.name}."
            }, status=401)

    # verify pin if student has one set
    if pin and student.pin and student.pin != pin:
        return JsonResponse({
            "error": "INVALID_PIN",
            "message": "Incorrect PIN."
        }, status=401)

    # verify account and validity
    if student.status != 'Active':
        return JsonResponse({
            "error": "ACCOUNT_INACTIVE",
            "message": f"Student account is currently {student.status}."
        }, status=403)

    if student.validity_status == 'Expired':
        return JsonResponse({
            "error": "VALIDITY_EXPIRED",
            "message": "Calling validity has expired. Recharge required."
        }, status=403)

    # get duration limits and allowed contacts
    dur_limits = CallingDurationEngine.resolve_limits(student)

    contacts = []
    seen_numbers = set()

    def add_contact(name, phone, relation):
        clean = "".join(filter(str.isdigit, str(phone or "")))
        if clean and clean not in seen_numbers:
            seen_numbers.add(clean)
            contacts.append({
                "name": name,
                "phone": phone,
                "relation": relation,
                "authorized": True
            })

    if student.primary_phone:
        add_contact(student.guardian_name or "Father", student.primary_phone, student.guardian_relation or "Father")
    if student.secondary_phone:
        add_contact("Mother", student.secondary_phone, "Mother")

    for g in student.guardian_contacts.filter(status='Active'):
        if g.father_phone:
            add_contact(g.name or "Father", g.father_phone, "Father")
        if g.mother_phone:
            add_contact("Mother", g.mother_phone, "Mother")

    student.code_last_used = timezone.now()
    student.save(update_fields=['code_last_used'])

    return JsonResponse({
        "status": "authenticated",
        "student": {
            "code": student.code,
            "name": student.name,
            "remaining_minutes": student.remaining_minutes,
            "validity_expiry": student.validity_expiry.strftime("%Y-%m-%d") if student.validity_expiry else None,
            "daily_limit_minutes": dur_limits.get("effective_daily_cap", student.daily_limit_min or 30),
        },
        "max_call_seconds": dur_limits.get("hard_max_call_duration", 15) * 60,
        "contacts": contacts,
    })


def student_profile(request, student_code):
    """Fetch student quota, minutes balance, and calling status."""
    student = Student.objects.filter(
        Q(code=student_code) | Q(calling_code=student_code)
    ).select_related('school').first()
    if not student:
        return JsonResponse({"error": "STUDENT_NOT_FOUND", "message": "Student not found."}, status=404)

    dur_limits = CallingDurationEngine.resolve_limits(student)
    allowed_in_sched, sched_reason, window_type = CallingScheduleEngine.is_call_allowed(student)

    # Calculate minutes used today
    today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_usage = CallRecord.objects.filter(
        student=student,
        start_time__gte=today_start,
        call_status='Completed'
    ).aggregate(total=Sum('minutes_deducted'))['total'] or 0

    return JsonResponse({
        "status": "success",
        "student": {
            "code": student.code,
            "name": student.name,
            "remaining_minutes": student.remaining_minutes,
            "validity_status": student.validity_status,
            "validity_expiry": student.validity_expiry.strftime("%Y-%m-%d") if student.validity_expiry else None,
            "daily_limit_minutes": dur_limits.get("effective_daily_cap", student.daily_limit_min or 30),
            "minutes_used_today": today_usage,
            "calling_allowed": allowed_in_sched,
        }
    })


def student_validity(request, student_code):
    """Check student calling validity, remaining minutes, and available recharge packs."""
    student = Student.objects.filter(
        Q(code=student_code) | Q(calling_code=student_code)
    ).select_related('school').first()
    if not student:
        return JsonResponse({"error": "STUDENT_NOT_FOUND", "message": f"Student '{student_code}' not found."}, status=404)

    eval_res = ValidityService.evaluate(student)
    validity_status = eval_res.get("status", "Active")
    days_left = eval_res.get("days_left", 0)
    is_usable = eval_res.get("is_usable", True)

    calling_allowed = bool(
        is_usable and
        student.status == 'Active' and
        student.code_status == 'Active' and
        student.remaining_minutes > 0
    )

    recharge_required = bool(
        validity_status in ["Expiring", "Grace Period", "Expired"] or
        student.remaining_minutes <= 10
    )

    plans = RechargePlan.objects.filter(status='Active').order_by('price')[:4]
    recharge_plans = [
        {
            "plan_code": p.code,
            "name": p.name,
            "price": float(p.price),
            "validity_days": p.validity_days,
            "minutes": p.minutes_allocated,
            "badge": p.badge_text or ""
        }
        for p in plans
    ]

    return JsonResponse({
        "student_code": student.code,
        "name": student.name,
        "school": student.school.code if student.school else "",
        "validity_status": validity_status,
        "validity_expiry": student.validity_expiry.strftime("%Y-%m-%d") if student.validity_expiry else None,
        "days_remaining": days_left,
        "calling_allowed": calling_allowed,
        "remaining_minutes": student.remaining_minutes,
        "wallet_balance": float(student.wallet_balance),
        "recharge_required": recharge_required,
        "recharge_plans": recharge_plans
    }, status=200)


def student_schedule_verification(request, student_code):
    """Check if the student is currently allowed to make calls based on active schedule."""
    student = Student.objects.filter(
        Q(code=student_code) | Q(calling_code=student_code)
    ).select_related('school').first()
    if not student:
        return JsonResponse({"error": "STUDENT_NOT_FOUND", "message": "Student not found."}, status=404)

    now = timezone.localtime()
    current_day = CallingScheduleEngine.DAY_ABBREVIATIONS[now.weekday()]
    allowed_in_sched, reason, window_type = CallingScheduleEngine.is_call_allowed(student, check_dt=now)

    school = student.school
    schedules = CallingScheduleRule.objects.filter(
        Q(school=school) | Q(school__isnull=True),
        is_active=True
    ).order_by('start_time')

    active_rule = None
    for s in schedules:
        days = [d.strip().upper() for d in s.days_of_week.split(',')]
        if current_day in days or "ALL" in days or ("MON-FRI" in s.days_of_week and current_day in ["MON", "TUE", "WED", "THU", "FRI"]):
            if s.start_time <= now.time() <= s.end_time:
                active_rule = s
                break

    schedule_list = [
        {
            "name": s.name,
            "policy_type": s.policy_type,
            "start_time": s.start_time.strftime("%H:%M"),
            "end_time": s.end_time.strftime("%H:%M"),
            "days": s.days_of_week
        }
        for s in schedules
    ]

    return JsonResponse({
        "status": "success",
        "student_code": student.code,
        "student_name": student.name,
        "school": school.name if school else "",
        "current_time": now.strftime("%H:%M"),
        "current_day": current_day,
        "calling_allowed": allowed_in_sched,
        "window_type": window_type,
        "reason": reason,
        "active_window": {
            "name": active_rule.name,
            "policy_type": active_rule.policy_type,
            "start_time": active_rule.start_time.strftime("%H:%M"),
            "end_time": active_rule.end_time.strftime("%H:%M")
        } if active_rule else None,
        "calling_schedules": schedule_list
    }, status=200)


def student_call_history(request, student_code):
    """Return recent call history for a student."""
    student = Student.objects.filter(
        Q(code=student_code) | Q(calling_code=student_code)
    ).first()
    if not student:
        return JsonResponse({"error": "STUDENT_NOT_FOUND", "message": "Student not found."}, status=404)

    try:
        limit = min(max(1, int(request.GET.get('limit') or 20)), 100)
    except (ValueError, TypeError):
        limit = 20

    records = CallRecord.objects.filter(student=student).order_by('-start_time')[:limit]

    history = []
    for r in records:
        history.append({
            "call_id": r.call_id,
            "destination_number": r.destination_number,
            "call_type": r.call_type,
            "start_time": r.start_time.isoformat() if r.start_time else None,
            "duration_seconds": r.duration_seconds or 0,
            "minutes_deducted": r.minutes_deducted,
            "status": r.call_status,
        })

    return JsonResponse({
        "status": "success",
        "student_code": student.code,
        "total_calls": CallRecord.objects.filter(student=student).count(),
        "history": history
    })


def student_contacts(request, student_code):
    """Returns whitelisted guardian contacts for a student."""
    student = Student.objects.filter(
        Q(code=student_code) | Q(calling_code=student_code)
    ).first()
    if not student:
        return JsonResponse({"error": "STUDENT_NOT_FOUND", "message": "Student not found."}, status=404)

    contacts = []
    seen = set()

    def add(name, phone, rel):
        clean = "".join(filter(str.isdigit, str(phone or "")))
        if clean and clean not in seen:
            seen.add(clean)
            contacts.append({"name": name, "phone": phone, "relation": rel})

    if student.primary_phone:
        add(student.guardian_name or "Primary Guardian", student.primary_phone, student.guardian_relation or "Guardian")
    if student.secondary_phone:
        add("Secondary Contact", student.secondary_phone, "Secondary Guardian")
    for g in student.guardian_contacts.filter(status='Active'):
        if g.father_phone:
            add(g.name or "Father", g.father_phone, "Father")
        if g.mother_phone:
            add("Mother", g.mother_phone, "Mother")

    return JsonResponse({
        "student_code": student.code,
        "contacts": contacts
    })


def student_whitelist_check(request, student_id):
    """Legacy/compatibility whitelist check endpoint."""
    phone = request.GET.get('phone', '')
    student = Student.objects.filter(Q(id=student_id) if student_id.isdigit() else Q(code=student_id)).first()
    if not student:
        return JsonResponse({"authorized": False, "message": "Student not found."}, status=404)

    authorized, max_seconds, reason = CallAuthorizationEngine.authorize_call(student, phone)
    return JsonResponse({
        "student_id": student.id,
        "student_code": student.code,
        "phone": phone,
        "authorized": authorized,
        "max_duration_seconds": max_seconds,
        "message": reason
    })


@csrf_exempt
def call_authorize(request):
    """Validate call permissions and generate session token."""
    if request.method != "POST":
        return JsonResponse({"error": "METHOD_NOT_ALLOWED", "message": "POST required."}, status=405)

    data = _parse_request_data(request)
    student_code = (data.get('student_code') or '').strip()
    dialed_number = (data.get('dialed_number') or data.get('phone') or '').strip()
    device_id = (data.get('device_id') or 'Kiosk Booth').strip()

    result = CallSessionManager.initiate_session(student_code, dialed_number, device_id=device_id)
    if result.get('authorized'):
        return JsonResponse({
            "authorized": True,
            "session_token": result.get("session_token"),
            "max_seconds": result.get("max_allowed_seconds", 0),
            "recipient_name": result.get("recipient_name", ""),
        }, status=200)
    else:
        return JsonResponse({
            "authorized": False,
            "reason": result.get("reason", "Call not authorized.")
        }, status=403)


@csrf_exempt
def call_terminate(request):
    """Record call end, deduct minutes, and save record."""
    if request.method != "POST":
        return JsonResponse({"error": "METHOD_NOT_ALLOWED", "message": "POST required."}, status=405)

    data = _parse_request_data(request)
    student_code = (data.get('student_code') or '').strip()
    dialed_number = (data.get('dialed_number') or '').strip()
    duration_seconds = int(data.get('duration_seconds') or 0)
    termination_reason = data.get('termination_reason') or 'Completed'
    device_id = data.get('device_id') or 'Kiosk Booth'

    result = CallSessionManager.terminate_session(
        student_code,
        dialed_number,
        duration_seconds=duration_seconds,
        termination_reason=termination_reason,
        device_id=device_id
    )
    if not result.get("success"):
        return JsonResponse({
            "status": "error",
            "message": result.get("error", "Call termination failed.")
        }, status=400)

    return JsonResponse({
        "status": "success",
        "call_id": result.get("call_id"),
        "minutes_deducted": result.get("minutes_deducted", 0),
        "remaining_minutes": result.get("remaining_minutes", 0),
    }, status=200)


def device_config(request, device_id):
    """Fetch device config, calling schedule, and duration settings."""
    device = KioskDevice.objects.filter(device_id=device_id).select_related('school', 'assigned_student').first()
    if not device:
        return JsonResponse({"error": "DEVICE_NOT_FOUND", "message": f"Device '{device_id}' not registered."}, status=404)

    student = device.assigned_student
    school = device.school

    limits = CallingDurationEngine.resolve_limits(student) if student else {
        "effective_per_call_limit": 15,
        "effective_daily_cap": 15
    }

    schedules = CallingScheduleRule.objects.filter(
        Q(school=school) | Q(school__isnull=True),
        is_active=True
    ).order_by('start_time')
    schedule_data = [
        {
            "name": s.name,
            "policy_type": s.policy_type,
            "start_time": s.start_time.strftime("%H:%M"),
            "end_time": s.end_time.strftime("%H:%M"),
            "days": s.days_of_week
        }
        for s in schedules
    ]

    warden = HostelWarden.objects.filter(school=school, status='On Duty').first()
    emergency_number = warden.phone if warden else (student.primary_phone if student else "+91 98101 23481")

    return JsonResponse({
        "device_id": device.device_id,
        "name": device.name,
        "school": school.code,
        "kiosk_mode_locked": device.kiosk_mode_locked,
        "assignment_type": device.assignment_type,
        "assigned_student": student.code if student else None,
        "heartbeat_interval_sec": 60,
        "max_call_duration_min": limits.get("effective_per_call_limit", 15),
        "daily_cumulative_limit_min": limits.get("effective_daily_cap", 15),
        "calling_schedules": schedule_data,
        "emergency_number": emergency_number
    }, status=200)


@csrf_exempt
def student_bulk_sync(request, school_code):
    """Import or update student and guardian list in bulk."""
    if request.method != "POST":
        return JsonResponse({"error": "METHOD_NOT_ALLOWED", "message": "POST required."}, status=405)

    school = School.objects.filter(code=school_code).first()
    if not school:
        return JsonResponse({"error": "SCHOOL_NOT_FOUND", "message": f"School '{school_code}' not found."}, status=404)

    data = _parse_request_data(request)
    students_data = data.get('students')
    if not isinstance(students_data, list):
        return JsonResponse({"error": "INVALID_PAYLOAD", "message": "'students' must be a list of student records."}, status=400)

    created_count = 0
    updated_count = 0
    errors = []

    with transaction.atomic():
        for idx, sdata in enumerate(students_data):
            code = (sdata.get('code') or '').strip()
            name = (sdata.get('name') or '').strip()
            if not code or not name:
                errors.append(f"Row {idx}: Missing student 'code' or 'name'.")
                continue

            primary_phone = (sdata.get('primary_phone') or sdata.get('phone') or '').strip()
            guardian_name = (sdata.get('guardian_name') or 'Primary Guardian').strip()
            guardian_rel = (sdata.get('guardian_relation') or 'Father').strip()
            class_name = (sdata.get('class_name') or 'General').strip()
            section = (sdata.get('section') or 'Section A').strip()
            pin = (sdata.get('pin') or '1234').strip()
            minutes = int(sdata.get('remaining_minutes') or 120)

            student = Student.objects.filter(code=code).first()
            if student:
                student.name = name
                student.school = school
                student.class_name = class_name
                student.section = section
                if primary_phone:
                    student.primary_phone = primary_phone
                if guardian_name:
                    student.guardian_name = guardian_name
                if guardian_rel:
                    student.guardian_relation = guardian_rel
                if pin:
                    student.pin = pin
                student.save()
                updated_count += 1
            else:
                student = Student.objects.create(
                    code=code,
                    calling_code=f"S2D-{school.code[:3]}-{code[-4:]}",
                    name=name,
                    school=school,
                    class_name=class_name,
                    section=section,
                    guardian_name=guardian_name,
                    guardian_relation=guardian_rel,
                    primary_phone=primary_phone or "+91 98000 00000",
                    pin=pin,
                    remaining_minutes=minutes,
                    status="Active",
                    validity_expiry=timezone.now().date() + timedelta(days=90)
                )
                created_count += 1

            if primary_phone:
                grd = Guardian.objects.filter(student=student).first()
                if not grd:
                    Guardian.objects.create(
                        school=school,
                        student=student,
                        code=f"GRD-{student.code}",
                        name=guardian_name,
                        relation=guardian_rel,
                        father_phone=primary_phone if guardian_rel == 'Father' else '',
                        mother_phone=primary_phone if guardian_rel == 'Mother' else '',
                        emergency_phone=primary_phone,
                        status='Active'
                    )

    return JsonResponse({
        "status": "success",
        "school_code": school.code,
        "total_processed": len(students_data),
        "created": created_count,
        "updated": updated_count,
        "errors": errors
    }, status=200)


@csrf_exempt
def payment_webhook(request):
    """Process recharge payment confirmation and credit student balance."""
    if request.method != "POST":
        return JsonResponse({"error": "METHOD_NOT_ALLOWED", "message": "POST required."}, status=405)

    data = _parse_request_data(request)
    student_code = (data.get('student_code') or '').strip()
    plan_code = (data.get('plan_code') or '').strip()
    recharge_id = (data.get('recharge_id') or data.get('transaction_id') or f"RCG-PG-{uuid.uuid4().hex[:8].upper()}").strip()
    amount = float(data.get('amount') or 0.0)

    student = Student.objects.filter(code=student_code).select_related('school').first()
    if not student:
        return JsonResponse({"error": "STUDENT_NOT_FOUND", "message": f"Student '{student_code}' not found."}, status=404)

    plan = RechargePlan.objects.filter(code=plan_code).first() if plan_code else None
    if plan:
        minutes_to_add = plan.minutes_allocated
        days_to_add = plan.validity_days
        plan_name = plan.name
        if not amount:
            amount = float(plan.price)
    else:
        minutes_to_add = int(data.get('minutes_added') or (amount * 2) or 100)
        days_to_add = int(data.get('validity_days_added') or 30)
        plan_name = "Online Payment Top-up"

    with transaction.atomic():
        recharge, created = StudentRecharge.objects.get_or_create(
            recharge_id=recharge_id,
            defaults={
                "student": student,
                "school": student.school,
                "plan": plan,
                "plan_name_cache": plan_name,
                "amount": amount,
                "minutes_added": minutes_to_add,
                "validity_days_added": days_to_add,
                "payment_mode": data.get("payment_mode") or "Payment Gateway Webhook",
                "status": "Successful"
            }
        )

        student.remaining_minutes += minutes_to_add
        today = timezone.now().date()
        base_expiry = student.validity_expiry if (student.validity_expiry and student.validity_expiry > today) else today
        student.validity_expiry = base_expiry + timedelta(days=days_to_add)
        student.save(update_fields=['remaining_minutes', 'validity_expiry'])

    return JsonResponse({
        "status": "success",
        "recharge_id": recharge.recharge_id,
        "student_code": student.code,
        "minutes_added": minutes_to_add,
        "new_remaining_minutes": student.remaining_minutes,
        "validity_expiry": student.validity_expiry.strftime("%Y-%m-%d")
    }, status=200)


@csrf_exempt
def student_emergency_sos(request):
    """Dispatch emergency alert to on-duty warden and emergency contacts."""
    if request.method != "POST":
        return JsonResponse({"error": "METHOD_NOT_ALLOWED", "message": "POST required."}, status=405)

    data = _parse_request_data(request)
    student_code = (data.get('student_code') or '').strip()
    device_id = (data.get('device_id') or 'Kiosk Device').strip()
    location = (data.get('location') or 'Hostel Campus').strip()

    student = Student.objects.filter(code=student_code).select_related('school').first()
    if not student:
        return JsonResponse({"error": "STUDENT_NOT_FOUND", "message": f"Student '{student_code}' not found."}, status=404)

    warden = HostelWarden.objects.filter(school=student.school, status='On Duty').first()
    school_emerg = student.school.primary_emergency_phone or student.school.warden_escalation_phone or "+91 98101 23481"
    warden_phone = warden.phone if warden else school_emerg
    warden_name = warden.name if warden else "Campus Security Desk"

    sos_id = f"SOS-{timezone.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:4].upper()}"

    CallRecord.objects.create(
        call_id=sos_id,
        school=student.school,
        student=student,
        destination_number=warden_phone,
        call_type='Emergency',
        device_id=device_id,
        duration_seconds=0,
        minutes_deducted=0,
        call_status='Completed'
    )

    return JsonResponse({
        "status": "emergency_broadcast_active",
        "alert_id": sos_id,
        "student_code": student.code,
        "student_name": student.name,
        "location": location,
        "warden_contacted": {
            "name": warden_name,
            "phone": warden_phone,
            "hostel_block": warden.hostel_block if warden else student.hostel_wing
        },
        "campus_police_phone": school_emerg,
        "emergency_contacts": [
            {
                "name": student.guardian_name,
                "phone": student.primary_phone,
                "relation": student.guardian_relation
            }
        ]
    }, status=200)


def school_call_data(request, school_code):
    """Return call logs and summary statistics for a school."""
    school = School.objects.filter(code=school_code).first()
    if not school:
        return JsonResponse({"error": "SCHOOL_NOT_FOUND", "message": f"School '{school_code}' not found."}, status=404)

    qs = CallRecord.objects.filter(school=school).select_related('student')

    student_code = request.GET.get('student_code')
    if student_code:
        qs = qs.filter(student__code=student_code)

    status_filter = request.GET.get('status')
    if status_filter:
        qs = qs.filter(call_status=status_filter)

    start_date = request.GET.get('start_date')
    if start_date:
        qs = qs.filter(start_time__date__gte=start_date)

    end_date = request.GET.get('end_date')
    if end_date:
        qs = qs.filter(start_time__date__lte=end_date)

    total_calls = qs.count()
    total_minutes = qs.aggregate(Sum('minutes_deducted'))['minutes_deducted__sum'] or 0

    try:
        limit = min(int(request.GET.get('limit', 50)), 200)
    except ValueError:
        limit = 50

    records = [
        {
            "call_id": r.call_id,
            "student_code": r.student.code,
            "student_name": r.student.name,
            "destination_number": r.destination_number,
            "call_type": r.call_type,
            "duration_seconds": r.duration_seconds,
            "minutes_deducted": r.minutes_deducted,
            "call_status": r.call_status,
            "start_time": r.start_time.isoformat()
        }
        for r in qs[:limit]
    ]

    return JsonResponse({
        "school_code": school.code,
        "total_calls": total_calls,
        "total_minutes": total_minutes,
        "records": records
    }, status=200)