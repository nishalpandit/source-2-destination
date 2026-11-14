"""
Super Admin Environment Views
Source 2 Destination — Global Governance Portal
Handles all Super Admin UI views, dynamic school management, and institutional KPI metrics.
"""
import os
import json
from django.shortcuts import render, redirect
from django.http import Http404, HttpResponseBadRequest
from django.template.loader import get_template
from django.template import TemplateDoesNotExist
from django.db.models import Sum, Count, Q
from .models import (
    School, Franchise, Student, GlobalDurationRule, CampusDurationRule,
    CallingScheduleRule, GlobalValidityRule, RechargePlan, StudentRecharge,
    ValidityExtensionLog
)
from .calling_services import (
    get_global_duration_rule, get_global_validity_rule,
    CallingDurationEngine, CallingScheduleEngine, ValidityService, RechargeService
)


def dashboard(request):
    """Render Super Admin Primary Dashboard with live system metrics."""
    total_campuses = School.objects.count()
    active_campuses = School.objects.filter(status='Active').count()
    db_students_count = Student.objects.count()
    total_students = db_students_count if db_students_count > 0 else (School.objects.aggregate(total=Sum('enrolled_students'))['total'] or 0)
    db_active_count = Student.objects.filter(status='Active').count()
    active_students = db_active_count if db_active_count > 0 else (School.objects.aggregate(total=Sum('active_students'))['total'] or 0)
    franchises_count = Franchise.objects.filter(status='Active').count()
    recent_students = Student.objects.select_related('school').order_by('-id')[:5]

    context = {
        "total_campuses": total_campuses,
        "active_campuses": active_campuses,
        "total_students": total_students,
        "active_students": active_students,
        "franchises_count": franchises_count,
        "recent_students": recent_students,
    }
    return render(request, 'super-admin/dashboard.html', context)


def schools_list(request):
    """
    Super Admin: Dynamic School Directory & Management
    Computes real-time campus statistics and provides server-side data bindings.
    """
    total_campuses = School.objects.count()
    active_campuses = School.objects.filter(status='Active').count()
    suspended_campuses = School.objects.filter(status='Suspended').count()
    total_enrolled = School.objects.aggregate(total=Sum('enrolled_students'))['total'] or 0
    avg_per_campus = int(total_enrolled / total_campuses) if total_campuses > 0 else 0
    expiring_subs = School.objects.filter(subscription_status='Expiring').count()
    franchises = list(Franchise.objects.filter(status='Active').values('code', 'name'))
    schools_qs = School.objects.select_related('franchise').order_by('-id')

    schools_data = [
        {
            "id": s.code,
            "code": s.code,
            "name": s.name,
            "city": s.city,
            "franchise": s.franchise.name if s.franchise else s.franchise_name_cache or "Unassigned",
            "adminName": s.admin_name,
            "adminEmail": s.admin_email,
            "students": s.enrolled_students or s.student_seats,
            "studentSeats": s.student_seats,
            "activeStudents": s.active_students,
            "subscriptionPlan": s.subscription_plan,
            "subscriptionStatus": s.subscription_status,
            "status": s.status
        }
        for s in schools_qs
    ]

    context = {
        "schools": schools_qs,
        "schools_json": json.dumps(schools_data),
        "total_campuses": total_campuses,
        "active_campuses": active_campuses,
        "suspended_campuses": suspended_campuses,
        "total_enrolled": f"{total_enrolled:,}",
        "avg_per_campus": avg_per_campus,
        "expiring_subs": expiring_subs,
        "franchises": franchises,
        "franchise_count": len(franchises)
    }
    return render(request, 'super-admin/schools/list.html', context)


def school_add(request):
    """Super Admin: Provision and register a new campus tenant."""
    if request.method == "POST":
        name = request.POST.get('name', '').strip()
        code = request.POST.get('code', '').strip()
        city = request.POST.get('city', '').strip()

        if not name or not city:
            return HttpResponseBadRequest("Name and City are required fields.")

        # Ensure unique code
        if not code:
            code = f"SCH-{School.objects.count() + 1001}"
        elif School.objects.filter(code=code).exists():
            code = f"{code}-{School.objects.count() + 1}"

        franchise_id = request.POST.get('franchise_id')
        franchise = Franchise.objects.filter(Q(code=franchise_id) | Q(id=franchise_id if str(franchise_id).isdigit() else 0)).first()

        seats = int(request.POST.get('student_seats') or 550)
        daily_cap = int(request.POST.get('daily_duration_cap') or 15)
        status = "Active" if request.POST.get('activate_immediately') else "Suspended"

        school = School.objects.create(
            code=code,
            name=name,
            campus_type=request.POST.get('campus_type', 'Co-ed Residential Boarding'),
            affiliation_board=request.POST.get('affiliation_board', 'CBSE'),
            website=request.POST.get('website', ''),
            city=city,
            state=request.POST.get('state', 'CT'),
            postal_code=request.POST.get('postal_code', ''),
            country=request.POST.get('country', 'United States'),
            address=request.POST.get('address', ''),
            timezone=request.POST.get('timezone', 'America/New_York'),
            hostel_blocks_count=int(request.POST.get('hostel_blocks_count') or 4),
            franchise=franchise,
            franchise_name_cache=franchise.name if franchise else '',
            admin_name=request.POST.get('admin_name', 'Campus Administrator'),
            admin_email=request.POST.get('admin_email', 'admin@institution.edu'),
            admin_phone=request.POST.get('admin_phone', ''),
            secondary_contact_name=request.POST.get('secondary_contact_name', ''),
            secondary_contact_email=request.POST.get('secondary_contact_email', ''),
            secondary_contact_phone=request.POST.get('secondary_contact_phone', ''),
            subscription_plan=request.POST.get('subscription_plan', 'Enterprise Boarding Annual'),
            billing_cycle=request.POST.get('billing_cycle', 'Annually'),
            student_seats=seats,
            enrolled_students=seats,
            active_students=seats if status == 'Active' else 0,
            daily_duration_cap=daily_cap,
            calling_window_start=request.POST.get('calling_window_start', '17:00'),
            calling_window_end=request.POST.get('calling_window_end', '19:30'),
            allowed_calling_days=request.POST.get('allowed_calling_days', 'All 7 Days'),
            emergency_calling_allowed=bool(request.POST.get('emergency_calling_allowed')),
            kiosk_group_tag=request.POST.get('kiosk_group_tag', 'AE-HOSTEL-BOOTH'),
            status=status,
            subscription_status="Active"
        )
        return redirect('source2destination:super_admin_schools_list')

    # GET request
    franchises = Franchise.objects.filter(status='Active').order_by('name')
    context = {
        "franchises": franchises,
    }
    return render(request, 'super-admin/schools/add.html', context)


def school_edit(request, school_id=None):
    """Super Admin: Edit campus profile and configuration."""
    target_id = school_id or request.GET.get('id')
    school = School.objects.filter(Q(code=target_id) | Q(id=target_id if str(target_id).isdigit() else 0)).first()

    if not school:
        school = School.objects.first()

    if request.method == "POST":
        school.name = request.POST.get('name', school.name)
        school.city = request.POST.get('city', school.city)
        school.admin_phone = request.POST.get('phone', school.admin_phone)
        school.admin_name = request.POST.get('admin_name', school.admin_name)
        school.admin_email = request.POST.get('admin_email', school.admin_email)
        school.subscription_plan = request.POST.get('subscription_plan', school.subscription_plan)

        if 'status' in request.POST:
            school.status = request.POST.get('status')
            if school.status == 'Suspended':
                school.active_students = 0
            else:
                school.active_students = school.enrolled_students

        school.save()
        return redirect(f"/super-admin/schools/details.html?id={school.code}")

    franchises = Franchise.objects.filter(status='Active').order_by('name')
    context = {
        "school": school,
        "franchises": franchises
    }
    return render(request, 'super-admin/schools/edit.html', context)


def school_details(request, school_id=None):
    """Super Admin: 360-degree School dossier & management view."""
    target_id = school_id or request.GET.get('id')
    school = School.objects.filter(Q(code=target_id) | Q(id=target_id if str(target_id).isdigit() else 0)).select_related('franchise').first()

    if not school:
        school = School.objects.first()

    context = {
        "school": school,
        "monthly_minutes": f"{school.active_students * 65:,}m" if school else "0m",
    }
    return render(request, 'super-admin/schools/details.html', context)


def calling_duration(request):
    """Super Admin: View & edit platform-wide calling duration ceilings."""
    rule = get_global_duration_rule()

    if request.method == "POST":
        rule.default_call_duration = int(request.POST.get('default_call', rule.default_call_duration))
        rule.hard_max_call_duration = int(request.POST.get('max_call', rule.hard_max_call_duration))
        rule.max_daily_student_cap = int(request.POST.get('max_daily', rule.max_daily_student_cap))
        rule.max_weekly_student_cap = int(request.POST.get('max_weekly', rule.max_weekly_student_cap))
        rule.low_balance_warn_sec = int(request.POST.get('warn_sec', rule.low_balance_warn_sec))
        rule.save()
        return redirect('/super-admin/calling-duration/index.html')

    context = {
        "rule": rule,
    }
    return render(request, 'super-admin/calling-duration/index.html', context)


def calling_schedules(request):
    """Super Admin: Global & school calling schedule management."""
    schools = School.objects.all().order_by('name')
    baseline_schedules = CallingScheduleRule.objects.filter(school__isnull=True).order_by('start_time')

    context = {
        "schools": schools,
        "baseline_schedules": baseline_schedules,
    }
    return render(request, 'super-admin/calling-schedules/index.html', context)


def validity_rules(request):
    """Super Admin: Global student validity and expiration rules."""
    rule = get_global_validity_rule()

    if request.method == "POST":
        rule.grace_period_hours = int(request.POST.get('grace_hours', rule.grace_period_hours))
        rule.reminder_days = request.POST.get('reminder_days', rule.reminder_days)
        rule.preserve_unused_minutes = ('preserve_unused' in request.POST) or (request.POST.get('preserve_unused_minutes') == 'on')
        rule.auto_suspend_on_expiry = ('auto_suspend' in request.POST) or (request.POST.get('auto_suspend_on_expiry') == 'on')
        rule.save()
        return redirect('/super-admin/validity/rules.html')

    context = {
        "rule": rule,
    }
    return render(request, 'super-admin/validity/rules.html', context)


def validity_overview(request):
    """Super Admin: Monitor student calling accounts validity & bulk extension."""
    if request.method == "POST":
        school_code = request.POST.get('school')
        days = int(request.POST.get('days', 90))
        reason = request.POST.get('reason', 'Administrative term extension')
        school = School.objects.filter(code=school_code).first()
        ValidityService.bulk_extend(school, days, reason)
        return redirect('/super-admin/validity/overview.html')

    students_qs = Student.objects.select_related('school').order_by('-id')
    schools = School.objects.all().order_by('name')

    # Compute KPI statistics dynamically
    valid_active = 0
    expiring_soon = 0
    grace_period = 0
    expired = 0

    students_data = []
    for s in students_qs:
        v_info = ValidityService.evaluate(s)
        status = v_info["status"]
        if status == "Active":
            valid_active += 1
        elif status == "Expiring":
            expiring_soon += 1
        elif status == "Grace Period":
            grace_period += 1
        else:
            expired += 1

        students_data.append({
            "id": s.code,
            "name": s.name,
            "studentCode": s.calling_code,
            "school": s.school.name,
            "validityStart": s.validity_start.strftime("%Y-%m-%d") if s.validity_start else "-",
            "validityExpiry": s.validity_expiry.strftime("%Y-%m-%d") if s.validity_expiry else "-",
            "remainingMinutes": s.remaining_minutes,
            "validityStatus": status,
            "status": s.status,
        })

    context = {
        "schools": schools,
        "students": students_qs,
        "students_json": json.dumps(students_data),
        "total_count": students_qs.count(),
        "valid_active": valid_active,
        "expiring_soon": expiring_soon,
        "grace_period": grace_period,
        "expired": expired,
    }
    return render(request, 'super-admin/validity/overview.html', context)


def recharges_overview(request):
    """Super Admin: Recharge plans catalog and direct credit allocation."""
    if request.method == "POST":
        school_code = request.POST.get('school')
        plan_code = request.POST.get('plan')
        target_code = request.POST.get('target_code', '').strip()

        plan = RechargePlan.objects.filter(code=plan_code).first()
        student = Student.objects.filter(
            Q(code=target_code) | Q(calling_code=target_code)
        ).first()

        if plan and student:
            RechargeService.process_recharge(
                student=student,
                plan=plan,
                payment_mode="Super Admin Direct Credit Allocation",
                voucher_ref=f"ALLOC-{plan.code}"
            )
        return redirect('/super-admin/recharges/overview.html')

    plans = RechargePlan.objects.all().order_by('price')
    schools = School.objects.all().order_by('name')

    context = {
        "plans": plans,
        "schools": schools,
    }
    return render(request, 'super-admin/recharges/overview.html', context)


def recharge_create_plan(request):
    """Super Admin: Create or edit recharge plan."""
    plan_code = request.GET.get('plan')
    plan = RechargePlan.objects.filter(code=plan_code).first() if plan_code else None

    if request.method == "POST":
        name = request.POST.get('plan_name', '').strip()
        price = float(request.POST.get('price', 22.00))
        minutes = int(request.POST.get('minutes', 300))
        validity_days = int(request.POST.get('validity_days', 120))
        per_call_cap = int(request.POST.get('per_call_cap', 15))
        status = request.POST.get('status', 'Active')

        if plan:
            plan.name = name
            plan.price = price
            plan.minutes_allocated = minutes
            plan.validity_days = validity_days
            plan.per_call_cap = per_call_cap
            plan.status = status
            plan.save()
        else:
            code = f"RPL-{RechargePlan.objects.count() + 1:02d}"
            RechargePlan.objects.create(
                code=code,
                name=name,
                price=price,
                minutes_allocated=minutes,
                validity_days=validity_days,
                per_call_cap=per_call_cap,
                status=status
            )
        return redirect('/super-admin/recharges/overview.html')

    context = {
        "plan": plan,
    }
    return render(request, 'super-admin/recharges/create-plan.html', context)


def recharge_history(request):
    """Super Admin: Global recharge ledger."""
    recharges_qs = StudentRecharge.objects.select_related('student', 'school', 'plan').order_by('-created_at')

    recharges_data = [
        {
            "id": r.recharge_id,
            "date": r.created_at.strftime("%Y-%m-%d %H:%M"),
            "studentName": r.student.name,
            "studentCode": r.student.calling_code,
            "school": r.school.name,
            "planName": r.plan_name_cache,
            "minutesAdded": r.minutes_added,
            "validityDays": r.validity_days_added,
            "amount": float(r.amount),
            "status": r.status,
            "paymentMode": r.payment_mode,
            "voucherRef": r.voucher_ref,
        }
        for r in recharges_qs
    ]

    context = {
        "recharges": recharges_qs,
        "recharges_json": json.dumps(recharges_data),
    }
    return render(request, 'super-admin/recharges/history.html', context)


def render_admin_page(request, path):
    """Render any other Super Admin subpage dynamically."""
    clean_path = os.path.normpath(path).replace('\\', '/').strip('/')
    if clean_path.startswith('..'):
        raise Http404("Invalid template path")

    candidates = []
    if clean_path.endswith('.html'):
        candidates.append(f"super-admin/{clean_path}")
    else:
        candidates.extend([
            f"super-admin/{clean_path}.html",
            f"super-admin/{clean_path}/index.html",
            f"super-admin/{clean_path}",
        ])

    for template_name in candidates:
        try:
            get_template(template_name)
            return render(request, template_name)
        except (TemplateDoesNotExist, PermissionError):
            continue

    raise Http404(f"Super Admin template '{clean_path}' not found")
