"""
Super Admin Environment Views
Source 2 Destination — Global Governance Portal
Handles all Super Admin UI views, dynamic school management, and institutional KPI metrics.
"""
import os
import csv
import json
from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseBadRequest, JsonResponse
from django.template.loader import get_template
from django.template import TemplateDoesNotExist
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models import Sum, Count, Q, Avg, Min, Max
from .models import (
    School, Franchise, Student, GlobalDurationRule, CampusDurationRule,
    CallingScheduleRule, GlobalValidityRule, RechargePlan, StudentRecharge,
    ValidityExtensionLog, KioskDevice, DeviceAssignment, HostelWarden, CallRecord,
    SchoolAdminProfile, CampusSubscription, FinancialTransaction, SystemAuditLog,
    PlatformSetting
)
from .calling_services import (
    get_global_duration_rule, get_global_validity_rule,
    CallingDurationEngine, CallingScheduleEngine, ValidityService, RechargeService
)


def log_admin_action(actor="Super Admin", action_type="UPDATE", domain="General", target_id="", description="", ip="127.0.0.1"):
    try:
        SystemAuditLog.objects.create(
            actor=actor,
            actor_role="SUPER_ADMIN",
            action_type=action_type,
            target_domain=domain,
            target_id=str(target_id),
            description=description,
            ip_address=ip or "127.0.0.1"
        )
    except Exception:
        pass


def dashboard(request):
    """Render Super Admin Primary Dashboard with live system metrics."""
    total_campuses = School.objects.count()
    active_campuses = School.objects.filter(status='Active').count()
    active_school_percent = round((active_campuses / total_campuses * 100), 1) if total_campuses > 0 else 0.0

    total_students = Student.objects.count()
    active_students = Student.objects.filter(status='Active').count()

    franchises_count = Franchise.objects.filter(status='Active').count()
    total_minutes = Student.objects.aggregate(total=Sum('remaining_minutes'))['total'] or 0
    active_kiosks = KioskDevice.objects.filter(status='Online').count()
    total_kiosks = KioskDevice.objects.count()

    total_revenue_val = (FinancialTransaction.objects.filter(status='Successful').aggregate(total=Sum('amount'))['total'] or 0) + \
                        (StudentRecharge.objects.filter(status='Successful').aggregate(total=Sum('amount'))['total'] or 0)
    total_revenue = f"{int(total_revenue_val):,}" if total_revenue_val > 0 else "0"

    recent_schools = School.objects.select_related('franchise').order_by('-id')[:5]
    recent_recharges = StudentRecharge.objects.select_related('student', 'school', 'plan').order_by('-created_at')[:5]

    # Dynamic Dashboard Charts
    sub_plans = ['Enterprise Annual', 'Campus Growth', 'Standard Qtr', 'Suspended']
    sub_counts = []
    has_sub_data = False
    for plan in sub_plans:
        if plan == 'Suspended':
            c = School.objects.filter(subscription_status='Suspended').count()
        else:
            c = School.objects.filter(subscription_plan__iexact=plan).count()
        sub_counts.append(c)
        if c > 0:
            has_sub_data = True

    month_cats = []
    sub_rev_monthly = []
    rech_rev_monthly = []
    has_rev_data = False
    now = timezone.now()
    for i in range(11, -1, -1):
        m_date = (now.replace(day=1) - timedelta(days=i * 28)).replace(day=1)
        m_label = m_date.strftime("%b")
        month_cats.append(m_label)
        s_rev = FinancialTransaction.objects.filter(
            status='Successful', created_at__year=m_date.year, created_at__month=m_date.month
        ).aggregate(tot=Sum('amount'))['tot'] or 0
        r_rev = StudentRecharge.objects.filter(
            status='Successful', created_at__year=m_date.year, created_at__month=m_date.month
        ).aggregate(tot=Sum('amount'))['tot'] or 0
        sub_rev_monthly.append(int(s_rev))
        rech_rev_monthly.append(int(r_rev))
        if s_rev > 0 or r_rev > 0:
            has_rev_data = True

    sa_charts = {
        "revenueTrend": {
            "categories": month_cats if has_rev_data else [],
            "subscriptions": sub_rev_monthly if has_rev_data else [],
            "recharges": rech_rev_monthly if has_rev_data else []
        },
        "subscriptions": {
            "categories": sub_plans if has_sub_data else [],
            "data": sub_counts if has_sub_data else []
        }
    }

    context = {
        "total_campuses": total_campuses,
        "active_campuses": active_campuses,
        "active_school_percent": active_school_percent,
        "total_students": total_students,
        "active_students": active_students,
        "franchises_count": franchises_count,
        "total_minutes": total_minutes,
        "active_kiosks": active_kiosks,
        "total_kiosks": total_kiosks,
        "total_revenue": total_revenue,
        "recent_schools": recent_schools,
        "recent_recharges": recent_recharges,
        "sa_charts_json": json.dumps(sa_charts),
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
    total_enrolled = Student.objects.count()
    avg_per_campus = int(total_enrolled / total_campuses) if total_campuses > 0 else 0
    expiring_subs = School.objects.filter(subscription_status='Expiring').count()
    franchise_assigned_count = School.objects.filter(franchise__isnull=False).count()
    franchise_assigned_percent = f"{round((franchise_assigned_count / total_campuses * 100), 1)}%" if total_campuses > 0 else "0%"
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
        "franchise_assigned_percent": franchise_assigned_percent,
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
            state=request.POST.get('state', 'Uttarakhand'),
            postal_code=request.POST.get('postal_code', ''),
            country=request.POST.get('country', 'India'),
            address=request.POST.get('address', ''),
            timezone=request.POST.get('timezone', 'Asia/Kolkata'),
            hostel_blocks_count=int(request.POST.get('hostel_blocks_count') or 4),
            franchise=franchise,
            franchise_name_cache=franchise.name if franchise else '',
            admin_name=request.POST.get('admin_name', 'Campus Administrator'),
            admin_email=request.POST.get('admin_email', 'admin@institution.edu'),
            admin_phone=request.POST.get('admin_phone', ''),
            secondary_contact_name=request.POST.get('secondary_contact_name', ''),
            secondary_contact_email=request.POST.get('secondary_contact_email', ''),
            secondary_contact_phone=request.POST.get('secondary_contact_phone', ''),
            subscription_plan=request.POST.get('subscription_plan', 'Campus Growth Annual'),
            billing_cycle=request.POST.get('billing_cycle', 'Annually'),
            student_seats=seats,
            enrolled_students=seats,
            active_students=seats if status == 'Active' else 0,
            daily_duration_cap=daily_cap,
            calling_window_start=request.POST.get('calling_window_start', '17:00'),
            calling_window_end=request.POST.get('calling_window_end', '19:30'),
            allowed_calling_days=request.POST.get('allowed_calling_days', 'All 7 Days'),
            emergency_calling_allowed=True,
            status=status,
            subscription_status="Active"
        )

        # Create or update School Administrator login credentials
        admin_username = request.POST.get('username', '').strip()
        admin_password = request.POST.get('password', '').strip() or '12345'
        admin_email = request.POST.get('admin_email', '').strip() or f"admin@{code.lower()}.edu"
        admin_name = request.POST.get('admin_name', 'Campus Administrator').strip()

        if not admin_username:
            admin_username = f"admin_{code.lower().replace('-', '_')}"

        admin_user = User.objects.filter(username__iexact=admin_username).first()
        if not admin_user:
            admin_user = User.objects.create_user(
                username=admin_username,
                email=admin_email,
                password=admin_password,
                first_name=admin_name
            )
        else:
            admin_user.email = admin_email
            if admin_password:
                admin_user.set_password(admin_password)
            admin_user.save()

        SchoolAdminProfile.objects.update_or_create(
            user=admin_user,
            defaults={
                "school": school,
                "admin_id": f"ADM-{school.code}",
                "name": admin_name,
                "email": admin_email,
                "phone": request.POST.get('admin_phone', ''),
                "designation": "Campus Principal / Administrator",
                "status": "Active"
            }
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
    if not target_id:
        return redirect('/super-admin/schools/list.html')

    school = School.objects.filter(Q(code=target_id) | Q(id=target_id if str(target_id).isdigit() else 0)).first()
    if not school:
        return redirect('/super-admin/schools/list.html')

    if request.method == "POST" and school:
        # School details
        school.name = request.POST.get('name', school.name).strip()
        school.campus_type = request.POST.get('campus_type', school.campus_type)
        school.affiliation_board = request.POST.get('affiliation_board', school.affiliation_board)
        school.website = request.POST.get('website', school.website).strip()
        school.city = request.POST.get('city', school.city).strip()
        school.state = request.POST.get('state', school.state).strip()
        school.postal_code = request.POST.get('postal_code', school.postal_code).strip()
        school.country = request.POST.get('country', school.country).strip()
        if request.POST.get('hostel_blocks_count'):
            try:
                school.hostel_blocks_count = int(request.POST['hostel_blocks_count'])
            except ValueError:
                pass
        school.timezone = request.POST.get('timezone', school.timezone)
        school.address = request.POST.get('address', school.address).strip()

        # Franchise & principal
        franchise_id = request.POST.get('franchise_id') or request.POST.get('franchise')
        if franchise_id:
            new_franchise = Franchise.objects.filter(
                Q(code=franchise_id) | Q(name=franchise_id) | Q(id=franchise_id if str(franchise_id).isdigit() else 0)
            ).first()
            if new_franchise:
                school.franchise = new_franchise
                school.franchise_name_cache = new_franchise.name

        school.admin_name = (request.POST.get('admin_name') or request.POST.get('adminName', school.admin_name)).strip()
        school.admin_email = (request.POST.get('admin_email') or request.POST.get('adminEmail', school.admin_email)).strip()
        school.admin_phone = (request.POST.get('admin_phone') or request.POST.get('phone', school.admin_phone)).strip()
        school.secondary_contact_name = request.POST.get('secondary_contact_name', school.secondary_contact_name).strip()
        school.secondary_contact_email = request.POST.get('secondary_contact_email', school.secondary_contact_email).strip()
        school.secondary_contact_phone = request.POST.get('secondary_contact_phone', school.secondary_contact_phone).strip()

        # Subscription & calling caps
        school.subscription_plan = request.POST.get('subscription_plan', school.subscription_plan)
        school.billing_cycle = request.POST.get('billing_cycle', school.billing_cycle)
        if request.POST.get('student_seats'):
            try:
                school.student_seats = int(request.POST['student_seats'])
            except ValueError:
                pass
        if request.POST.get('daily_duration_cap'):
            try:
                school.daily_duration_cap = int(request.POST['daily_duration_cap'])
            except ValueError:
                pass
        if request.POST.get('calling_window_start'):
            school.calling_window_start = request.POST['calling_window_start']
        if request.POST.get('calling_window_end'):
            school.calling_window_end = request.POST['calling_window_end']
        if request.POST.get('allowed_calling_days'):
            school.allowed_calling_days = request.POST['allowed_calling_days']
        if request.POST.get('kiosk_group_tag'):
            school.kiosk_group_tag = request.POST['kiosk_group_tag']
        school.emergency_calling_allowed = request.POST.get('emergency_calling_allowed') == 'on' or request.POST.get('emergency_calling_allowed') is True

        # Caller ID & emergency numbers
        if request.POST.get('primary_emergency_phone'):
            school.primary_emergency_phone = request.POST['primary_emergency_phone'].strip()
        if request.POST.get('secondary_emergency_phone'):
            school.secondary_emergency_phone = request.POST['secondary_emergency_phone'].strip()
        if request.POST.get('warden_escalation_phone'):
            school.warden_escalation_phone = request.POST['warden_escalation_phone'].strip()
        if 'display_school_caller_id' in request.POST:
            school.display_school_caller_id = request.POST.get('display_school_caller_id') in ['on', 'true', True]
        if 'show_guardian_whitelist_numbers' in request.POST:
            school.show_guardian_whitelist_numbers = request.POST.get('show_guardian_whitelist_numbers') in ['on', 'true', True]
        if 'notify_sms_guardians' in request.POST:
            school.notify_sms_guardians = request.POST.get('notify_sms_guardians') in ['on', 'true', True]

        if 'status' in request.POST:
            school.status = request.POST.get('status')
            if school.status == 'Suspended':
                school.active_students = 0
            else:
                school.active_students = school.enrolled_students

        # Handle password & username update for school administrator
        school_pwd = request.POST.get('school_admin_password', '').strip()
        school_uname = request.POST.get('school_admin_username', '').strip()
        admin_prof = SchoolAdminProfile.objects.filter(school=school).select_related('user').first()
        if school_pwd or school_uname:
            if not admin_prof:
                uname = school_uname or school.code.lower()
                u = User.objects.filter(username=uname).first()
                if not u:
                    u = User.objects.create_user(username=uname, email=school.admin_email, password=school_pwd or "12345")
                elif school_pwd:
                    u.set_password(school_pwd)
                    u.save()
                admin_prof = SchoolAdminProfile.objects.create(
                    user=u,
                    school=school,
                    admin_id=f"ADM-{school.code.split('-')[-1] if '-' in school.code else school.id}",
                    name=school.admin_name,
                    email=school.admin_email,
                    phone=school.admin_phone,
                    designation="Principal / School Administrator",
                    status="Active"
                )
            else:
                u = admin_prof.user
                if not u:
                    uname = school_uname or school.code.lower()
                    u = User.objects.filter(username=uname).first()
                    if not u:
                        u = User.objects.create_user(username=uname, email=school.admin_email, password=school_pwd or "12345")
                    elif school_pwd:
                        u.set_password(school_pwd)
                        u.save()
                    admin_prof.user = u
                    admin_prof.save(update_fields=['user'])
                else:
                    if school_uname and school_uname != u.username:
                        if not User.objects.filter(username=school_uname).exclude(pk=u.pk).exists():
                            u.username = school_uname
                    if school_pwd:
                        u.set_password(school_pwd)
                    if school.admin_email and u.email != school.admin_email:
                        u.email = school.admin_email
                    u.save()

        school.save()
        return redirect(f"/super-admin/schools/details.html?id={school.code}")

    franchises = Franchise.objects.filter(status='Active').order_by('name')
    school_admin_profile = SchoolAdminProfile.objects.filter(school=school).select_related('user').first()
    context = {
        "school": school,
        "franchises": franchises,
        "school_admin_profile": school_admin_profile
    }
    return render(request, 'super-admin/schools/edit.html', context)


def school_details(request, school_id=None):
    """Super Admin: 360-degree School dossier & management view."""
    target_id = school_id or request.GET.get('id')
    if not target_id:
        return redirect('/super-admin/schools/list.html')

    school = School.objects.filter(Q(code=target_id) | Q(id=target_id if str(target_id).isdigit() else 0)).select_related('franchise').first()
    if not school:
        return redirect('/super-admin/schools/list.html')

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


# --- Franchise Partners ---

def franchises_list(request):
    """
    Super Admin: Fleet-wide Regional Franchise Partners Directory & Overview.
    """
    franchises_qs = Franchise.objects.all().order_by('name')
    total_franchises = franchises_qs.count()
    active_franchises = franchises_qs.filter(status='Active').count()
    total_schools = School.objects.filter(franchise__isnull=False).count()
    avg_comm = franchises_qs.aggregate(avg=Avg('commission_rate'))['avg']
    avg_commission = f"{avg_comm:.1f}%" if avg_comm is not None else "0.0%"
    min_comm = franchises_qs.aggregate(min=Min('commission_rate'))['min']
    max_comm = franchises_qs.aggregate(max=Max('commission_rate'))['max']
    commission_range = f"{min_comm:.1f}% – {max_comm:.1f}%" if min_comm is not None else "0.0%" 

    franchises_data = []
    for f in franchises_qs:
        assigned_schools_count = f.schools.count()
        enrolled_students_count = Student.objects.filter(school__franchise=f).count()
        franchises_data.append({
            "id": f.code,
            "pk": f.id,
            "name": f.name,
            "code": f.code,
            "partnerContact": f.partner_contact,
            "email": f.email,
            "phone": f.phone,
            "territory": f.territory,
            "commissionRate": float(f.commission_rate),
            "assignedSchools": assigned_schools_count,
            "enrolledStudents": enrolled_students_count,
            "status": f.status,
            "createdDate": f.created_at.strftime("%Y-%m-%d") if f.created_at else "2026-01-01"
        })

    context = {
        "franchises": franchises_qs,
        "franchises_json": json.dumps(franchises_data),
        "total_franchises": total_franchises,
        "active_franchises": active_franchises,
        "total_schools": total_schools,
        "avg_commission": avg_commission,
        "commission_range": commission_range,
    }
    return render(request, 'super-admin/franchises/list.html', context)


def franchise_add(request):
    """
    Super Admin: Onboard a new Regional Franchise Partner & Territory License.
    """
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        code = request.POST.get('code', '').strip().upper()
        partner_contact = request.POST.get('partner_contact', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        territory = request.POST.get('territory', '').strip()
        commission_rate = request.POST.get('commission_rate', '15.00').strip()
        status = request.POST.get('status', 'Active')

        if not code:
            code = f"FRN-{Franchise.objects.count() + 101}"

        franchise_username = request.POST.get('username', '').strip()
        franchise_password = request.POST.get('password', '').strip() or '12345'
        if not franchise_username:
            franchise_username = f"franchise_{code.lower().replace('-', '_')}"

        franchise_user = User.objects.filter(username__iexact=franchise_username).first()
        if not franchise_user:
            franchise_user = User.objects.create_user(
                username=franchise_username,
                email=email,
                password=franchise_password,
                first_name=partner_contact or name
            )
        else:
            franchise_user.email = email
            if franchise_password:
                franchise_user.set_password(franchise_password)
            franchise_user.save()

        franchise = Franchise.objects.create(
            code=code,
            name=name,
            partner_contact=partner_contact,
            email=email,
            phone=phone,
            territory=territory,
            commission_rate=float(commission_rate) if commission_rate else 15.00,
            status='Active' if status in ['Active', 'active'] else 'Suspended',
            user=franchise_user
        )

        log_admin_action(
            actor="Super Admin",
            action_type="CREATE",
            domain="Franchise",
            target_id=franchise.code,
            description=f"Onboarded regional franchise partner: {name} ({code}) covering {territory}"
        )
        return redirect('/super-admin/franchises/list.html')

    return render(request, 'super-admin/franchises/add.html')


def franchise_edit(request):
    """
    Super Admin: Edit Franchise Partner details, territory boundary & commission %.
    """
    target_id = request.GET.get('id', '') or request.POST.get('id', '')
    if not target_id:
        return redirect('/super-admin/franchises/list.html')

    franchise = Franchise.objects.filter(Q(code=target_id) | Q(pk=target_id if target_id.isdigit() else 0)).first()
    if not franchise:
        return redirect('/super-admin/franchises/list.html')

    if request.method == 'POST' and franchise:
        franchise.name = request.POST.get('name', franchise.name).strip()
        franchise.partner_contact = request.POST.get('partner_contact', franchise.partner_contact).strip()
        franchise.email = request.POST.get('email', franchise.email).strip()
        franchise.phone = request.POST.get('phone', franchise.phone).strip()
        franchise.territory = request.POST.get('territory', franchise.territory).strip()

        comm_val = request.POST.get('commission_rate', '')
        if comm_val:
            try:
                franchise.commission_rate = float(comm_val)
            except ValueError:
                pass

        status = request.POST.get('status', franchise.status)
        franchise.status = 'Active' if status in ['Active', 'active'] else 'Suspended'
        franchise.save()

        log_admin_action(
            actor="Super Admin",
            action_type="UPDATE",
            domain="Franchise",
            target_id=franchise.code,
            description=f"Updated franchise profile & commission rate for {franchise.name}"
        )
        return redirect('/super-admin/franchises/list.html')

    franchise_dict = {
        "id": franchise.code if franchise else "FRN-101",
        "name": franchise.name if franchise else "North India EduNet Partners",
        "partnerContact": franchise.partner_contact if franchise else "Vikramaditya Singhania",
        "email": franchise.email if franchise else "v.singhania@northedunet.in",
        "phone": franchise.phone if franchise else "+91 98101 22334",
        "territory": franchise.territory if franchise else "North India Boarding Corridor",
        "commissionRate": float(franchise.commission_rate) if franchise else 18.00,
        "status": franchise.status if franchise else "Active"
    }

    context = {
        "franchise": franchise,
        "franchise_json": json.dumps(franchise_dict),
    }
    return render(request, 'super-admin/franchises/edit.html', context)


def franchise_details(request):
    """
    Super Admin: Franchise 360° Territory Performance, Schools & Commission Ledger.
    """
    target_id = request.GET.get('id', '')
    if not target_id:
        return redirect('/super-admin/franchises/list.html')

    franchise = Franchise.objects.filter(Q(code=target_id) | Q(pk=target_id if target_id.isdigit() else 0)).first()
    if not franchise:
        return redirect('/super-admin/franchises/list.html')

    assigned_schools = franchise.schools.all().order_by('name') if franchise else []
    total_students = Student.objects.filter(school__franchise=franchise).count() if franchise else 0
    recent_transactions = FinancialTransaction.objects.filter(franchise=franchise).order_by('-created_at')[:20] if franchise else []

    franchise_dict = {
        "id": franchise.code if franchise else "FRN-101",
        "name": franchise.name if franchise else "North India EduNet Partners",
        "partnerContact": franchise.partner_contact if franchise else "Vikramaditya Singhania",
        "email": franchise.email if franchise else "v.singhania@northedunet.in",
        "phone": franchise.phone if franchise else "+91 98101 22334",
        "territory": franchise.territory if franchise else "North India Boarding Corridor",
        "commissionRate": float(franchise.commission_rate) if franchise else 18.00,
        "status": franchise.status if franchise else "Active",
        "schoolsCount": len(assigned_schools),
        "studentsCount": total_students
    }

    context = {
        "franchise": franchise,
        "franchise_json": json.dumps(franchise_dict),
        "assigned_schools": assigned_schools,
        "total_students": total_students,
        "recent_transactions": recent_transactions,
    }
    return render(request, 'super-admin/franchises/details.html', context)


# --- School Administrators ---

def school_admins_list(request):
    """
    Super Admin: Campus Administrator Fleet Directory & Telemetry.
    """
    admins_qs = SchoolAdminProfile.objects.select_related('school', 'user').order_by('-id')
    total_admins = admins_qs.count()
    active_admins = admins_qs.filter(status='Active').count()
    mfa_count = admins_qs.filter(mfa_enforced=True).count()
    mfa_percent = round((mfa_count / total_admins * 100), 1) if total_admins > 0 else 0.0
    pending_count = admins_qs.filter(status='Pending Onboarding').count()
    deactivated_count = admins_qs.filter(status='Deactivated').count()
    schools_count = School.objects.count()

    school_admins_data = [
        {
            "id": a.admin_id,
            "name": a.name,
            "email": a.email,
            "phone": a.phone,
            "designation": a.designation,
            "school": a.school.name,
            "schoolId": a.school.code,
            "mfaEnabled": "Enabled" if a.mfa_enforced else "Disabled",
            "lastLogin": a.last_active.strftime("%Y-%m-%d %H:%M"),
            "status": "Active" if a.status == "Active" else "Inactive"
        }
        for a in admins_qs
    ]

    context = {
        "admins": admins_qs,
        "school_admins_json": json.dumps(school_admins_data),
        "total_admins": total_admins,
        "active_admins": active_admins,
        "mfa_percent": mfa_percent,
        "pending_count": pending_count,
        "deactivated_count": deactivated_count,
        "schools_count": schools_count,
    }
    return render(request, 'super-admin/school-admins/list.html', context)


def school_admin_add(request):
    """
    Super Admin: Provision a new Campus Principal / Administrator.
    """
    schools = School.objects.all().order_by('name')
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        designation = request.POST.get('designation', 'Principal & Primary Admin').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        school_code = request.POST.get('school_id', '').strip()
        require_mfa = request.POST.get('require_mfa') in ['on', 'true', '1']

        school = School.objects.filter(Q(code=school_code) | Q(name__icontains=school_code)).first() or schools.first()
        if not school:
            return HttpResponseBadRequest("No valid campus found for assignment.")

        admin_id = f"ADM-{SchoolAdminProfile.objects.count() + 101}"

        # Create or update corresponding User account
        user, _ = User.objects.get_or_create(username=email, defaults={'email': email, 'first_name': name})

        profile = SchoolAdminProfile.objects.create(
            user=user,
            school=school,
            admin_id=admin_id,
            name=name,
            email=email,
            phone=phone,
            designation=designation,
            mfa_enforced=require_mfa,
            status='Active'
        )

        log_admin_action(
            actor="Super Admin",
            action_type="CREATE",
            domain="SchoolAdmin",
            target_id=profile.admin_id,
            description=f"Provisioned campus administrator {name} for {school.name}"
        )
        return redirect('/super-admin/school-admins/list.html')

    return render(request, 'super-admin/school-admins/add.html', {"schools": schools})


def school_admin_edit(request):
    """
    Super Admin: Edit Campus Administrator profile & assignment.
    """
    admin_id = request.GET.get('id', '') or request.POST.get('id', '')
    profile = SchoolAdminProfile.objects.filter(Q(admin_id=admin_id) | Q(pk=admin_id if admin_id.isdigit() else 0)).first()
    schools = School.objects.all().order_by('name')

    if not profile:
        profile = SchoolAdminProfile.objects.first()

    if request.method == 'POST' and profile:
        profile.name = request.POST.get('name', profile.name).strip()
        profile.designation = request.POST.get('designation', profile.designation).strip()
        profile.email = request.POST.get('email', profile.email).strip()
        profile.phone = request.POST.get('phone', profile.phone).strip()

        school_name = request.POST.get('school', '')
        if school_name:
            sch = School.objects.filter(Q(name__icontains=school_name) | Q(code=school_name)).first()
            if sch:
                profile.school = sch

        status = request.POST.get('status', 'Active')
        profile.status = 'Active' if status in ['Active', 'active'] else 'Deactivated'

        # Manage Portal Credentials & Password
        new_password = request.POST.get('password', '').strip()
        new_username = request.POST.get('username', '').strip()

        admin_user = profile.user
        if not admin_user and (new_username or profile.email):
            fallback_uname = new_username or profile.email.split('@')[0] or f"school_{profile.admin_id.lower()}"
            admin_user = User.objects.filter(username=fallback_uname).first()
            if not admin_user and profile.email:
                admin_user = User.objects.filter(email__iexact=profile.email).first()
            if not admin_user:
                admin_user = User.objects.create_user(
                    username=fallback_uname,
                    email=profile.email,
                    password=new_password or "12345"
                )
            profile.user = admin_user

        if admin_user:
            if new_username and new_username != admin_user.username:
                if not User.objects.filter(username=new_username).exclude(pk=admin_user.pk).exists():
                    admin_user.username = new_username
            if new_password:
                admin_user.set_password(new_password)
            if profile.email and admin_user.email != profile.email:
                admin_user.email = profile.email
            admin_user.save()

        profile.save()

        log_admin_action(
            actor="Super Admin",
            action_type="UPDATE",
            domain="SchoolAdmin",
            target_id=profile.admin_id,
            description=f"Updated profile for administrator {profile.name} ({profile.school.name})"
        )
        return redirect('/super-admin/school-admins/list.html')

    profile_dict = {
        "id": profile.admin_id if profile else "ADM-201",
        "name": profile.name if profile else "Dr. Ramesh Chandra Sharma",
        "designation": profile.designation if profile else "Principal & Primary Admin",
        "email": profile.email if profile else "principal@doonvalley.edu.in",
        "phone": profile.phone if profile else "+91 98101 23456",
        "school": profile.school.name if profile and profile.school else "Doon Valley Residential Academy",
        "status": profile.status if profile else "Active"
    }

    context = {
        "profile": profile,
        "profile_json": json.dumps(profile_dict),
        "schools": schools
    }
    return render(request, 'super-admin/school-admins/edit.html', context)


def school_admin_details(request):
    """
    Super Admin: 360° Dossier View of Campus Principal.
    """
    admin_id = request.GET.get('id', '')
    profile = SchoolAdminProfile.objects.filter(Q(admin_id=admin_id) | Q(pk=admin_id if admin_id.isdigit() else 0)).select_related('school').first()
    if not profile:
        profile = SchoolAdminProfile.objects.first()

    audit_logs = SystemAuditLog.objects.filter(
        Q(target_id=profile.admin_id if profile else '') | Q(actor=profile.name if profile else '')
    )[:5] if profile else []

    profile_dict = {
        "id": profile.admin_id if profile else "ADM-201",
        "name": profile.name if profile else "Dr. Ramesh Chandra Sharma",
        "designation": profile.designation if profile else "Principal & Primary Admin",
        "email": profile.email if profile else "principal@doonvalley.edu.in",
        "phone": profile.phone if profile else "+91 98101 23456",
        "school": profile.school.name if profile and profile.school else "Doon Valley Residential Academy",
        "mfaEnabled": "Enabled" if (profile and profile.mfa_enforced) else "Disabled",
        "lastLogin": profile.last_active.strftime("%Y-%m-%d %H:%M") if profile else "2026-11-10 08:42",
        "status": profile.status if profile else "Active"
    }

    context = {
        "profile": profile,
        "profile_json": json.dumps(profile_dict),
        "audit_logs": audit_logs,
    }
    return render(request, 'super-admin/school-admins/details.html', context)


# --- Kiosk Devices ---

def devices_list(request):
    """
    Super Admin: Fleet-wide Android Enterprise Kiosk Registry.
    """
    devices_qs = KioskDevice.objects.select_related('school').order_by('device_id')
    total_terminals = devices_qs.count()
    online_count = devices_qs.filter(status='Online').count()
    online_percent = round((online_count / total_terminals * 100), 1) if total_terminals > 0 else 0.0
    compliant_count = devices_qs.filter(kiosk_mode_locked=True).count()
    tamper_blocked_count = devices_qs.filter(status='Maintenance').count()

    devices_data = [
        {
            "id": d.device_id,
            "deviceName": d.name,
            "serialNumber": d.serial_number or d.device_id,
            "school": d.school.name,
            "wingLocation": f"{d.hostel_block} · {d.assigned_wing}",
            "enrollmentStatus": "Android Enterprise",
            "kioskCompliance": "Compliant" if d.kiosk_mode_locked else "Policy Update Pending",
            "onlineStatus": d.status,
            "lastHeartbeat": d.last_heartbeat.strftime("%Y-%m-%d %H:%M"),
            "status": "Active" if d.status != "Maintenance" else "Blocked"
        }
        for d in devices_qs
    ]

    context = {
        "devices": devices_qs,
        "devices_json": json.dumps(devices_data),
        "total_terminals": total_terminals,
        "online_count": online_count,
        "online_percent": online_percent,
        "compliant_count": compliant_count,
        "tamper_blocked_count": tamper_blocked_count,
    }
    return render(request, 'super-admin/devices/list.html', context)


def device_register(request):
    """
    Super Admin: Provision, register, or reassign an Android Enterprise Kiosk.
    """
    schools = School.objects.all().order_by('name')
    device_id = request.GET.get('id', '') or request.POST.get('device_id', '')
    device = KioskDevice.objects.filter(device_id=device_id).first() if device_id else None

    if request.method == 'POST':
        name = request.POST.get('deviceName', '').strip() or request.POST.get('name', '').strip()
        serial = request.POST.get('serialNumber', '').strip()
        imei = request.POST.get('imei', '').strip()
        school_code = request.POST.get('school', '').strip()
        wing = request.POST.get('wingLocation', 'Main Hostel Wing').strip()
        status = request.POST.get('status', 'Online').strip()

        school = School.objects.filter(Q(code=school_code) | Q(name__icontains=school_code)).first() or schools.first()

        if device:
            device.name = name or device.name
            device.serial_number = serial or device.serial_number
            device.imei = imei or device.imei
            if school:
                device.school = school
            device.assigned_wing = wing
            device.status = 'Online' if status in ['Online', 'Active'] else 'Maintenance'
            device.save()
            action_type = "UPDATE"
        else:
            new_id = f"DEV-{KioskDevice.objects.count() + 7701}"
            device = KioskDevice.objects.create(
                device_id=new_id,
                school=school,
                name=name or f"Hostel Booth {new_id}",
                serial_number=serial or f"SN-{new_id}",
                imei=imei,
                hostel_block=wing,
                assigned_wing=wing,
                status='Online',
                kiosk_mode_locked=True
            )
            action_type = "CREATE"

        log_admin_action(
            actor="Super Admin",
            action_type=action_type,
            domain="KioskDevice",
            target_id=device.device_id,
            description=f"Registered/Updated kiosk booth {device.name} at {device.school.name}"
        )
        return redirect('/super-admin/devices/list.html')

    device_dict = {
        "id": device.device_id if device else "",
        "deviceName": device.name if device else "",
        "serialNumber": device.serial_number if device else "",
        "imei": device.imei if device else "",
        "school": device.school.code if device else "",
        "wingLocation": device.assigned_wing if device else "",
        "status": device.status if device else "Online"
    }

    return render(request, 'super-admin/devices/register.html', {
        "schools": schools,
        "device": device,
        "device_json": json.dumps(device_dict)
    })


def device_details(request):
    """
    Super Admin: Hardware Dossier & Live MDM Telemetry.
    """
    device_id = request.GET.get('id', '')
    device = KioskDevice.objects.filter(device_id=device_id).select_related('school').first()
    if not device:
        device = KioskDevice.objects.first()

    device_dict = {
        "id": device.device_id if device else "DEV-7701",
        "deviceName": device.name if device else "North Hall Booth 1",
        "serialNumber": device.serial_number if device else "SN-7701-S2D",
        "imei": device.imei if device else "864298031234567",
        "school": device.school.name if device else "Doon Valley Residential Academy",
        "wingLocation": device.assigned_wing if device else "North Wing",
        "onlineStatus": device.status if device else "Online",
        "batteryLevel": f"{device.battery_level}%" if device else "95%",
        "signalStrength": device.signal_strength if device else "4G LTE (-78 dBm)",
        "appVersion": device.app_version if (device and device.app_version) else "",
        "lastHeartbeat": device.last_heartbeat.strftime("%Y-%m-%d %H:%M") if device else "Just now"
    }

    recent_calls = CallRecord.objects.filter(
        Q(device_id=device.name) | Q(device_id=device.device_id)
    ).order_by('-start_time')[:10] if device else []

    context = {
        "device": device,
        "device_json": json.dumps(device_dict),
        "recent_calls": recent_calls
    }
    return render(request, 'super-admin/devices/details.html', context)


# --- Subscriptions & Payments ---

def subscriptions_overview(request):
    """
    Super Admin: Institutional SaaS Subscription Contracts & ARR Ledger.
    """
    subs_qs = CampusSubscription.objects.select_related('school', 'school__franchise').order_by('-id')
    arr_total_val = subs_qs.filter(status='Active').aggregate(t=Sum('contract_value'))['t'] or 0
    arr_total = f"₹{int(arr_total_val):,}" if arr_total_val > 0 else "₹0" 
    active_contracts = subs_qs.filter(status='Active').count()
    expiring_soon = subs_qs.filter(status='Expiring Soon').count()
    expired_contracts = subs_qs.filter(status__in=['Expired', 'Past Due']).count()

    subscriptions_data = [
        {
            "id": s.subscription_id,
            "school": s.school.name,
            "franchise": s.school.franchise.name if s.school.franchise else "Direct Institutional",
            "planName": s.plan_name,
            "studentSeats": s.student_seats,
            "deviceSeats": s.device_seats,
            "amount": float(s.contract_value),
            "expiryDate": s.expiry_date.strftime("%Y-%m-%d"),
            "autoRenew": "Auto-Renew Enabled" if s.auto_renew else "Manual Renewal",
            "status": s.status
        }
        for s in subs_qs
    ]

    context = {
        "subscriptions": subs_qs,
        "subscriptions_json": json.dumps(subscriptions_data),
        "arr_total": arr_total,
        "active_contracts": active_contracts,
        "expiring_soon": expiring_soon,
        "expired_contracts": expired_contracts,
    }
    return render(request, 'super-admin/subscriptions/overview.html', context)


def subscription_create(request):
    """
    Super Admin: Provision or renew campus subscription contracts.
    """
    schools = School.objects.all().order_by('name')
    if request.method == 'POST':
        school_code = request.POST.get('school', '').strip()
        plan_name = request.POST.get('planName', 'Enterprise Boarding Annual').strip()
        student_seats = int(request.POST.get('studentSeats', 750) or 750)
        device_seats = int(request.POST.get('deviceSeats', 35) or 35)
        expiry_date_str = request.POST.get('expiryDate', '').strip()

        school = School.objects.filter(Q(code=school_code) | Q(name__icontains=school_code)).first() or schools.first()

        contract_value = 840000.00
        if "5,90,000" in plan_name or "Growth" in plan_name:
            contract_value = 590000.00
        elif "1,85,000" in plan_name or "Quarterly" in plan_name:
            contract_value = 185000.00

        try:
            exp_date = timezone.datetime.strptime(expiry_date_str, "%Y-%m-%d").date()
        except Exception:
            exp_date = timezone.now().date() + timedelta(days=365)

        sub_id = f"SUB-{timezone.now().year}-{CampusSubscription.objects.count() + 101}"

        sub = CampusSubscription.objects.create(
            subscription_id=sub_id,
            school=school,
            plan_name=plan_name,
            tier='Enterprise Boarding' if 'Enterprise' in plan_name else 'Standard Campus',
            contract_value=contract_value,
            student_seats=student_seats,
            device_seats=device_seats,
            expiry_date=exp_date,
            auto_renew=True,
            status='Active'
        )

        # Generate financial transaction ledger entry
        FinancialTransaction.objects.create(
            transaction_id=f"TXN-{timezone.now().strftime('%Y%m%d')}-{FinancialTransaction.objects.count() + 101}",
            school=school,
            franchise=school.franchise,
            category="Annual Subscription",
            amount=contract_value,
            payment_method="NEFT / RTGS",
            gateway_reference=f"NEFT-SBIN-{sub_id}",
            payer_name=f"{school.name} Bursar Desk",
            status="Successful"
        )

        log_admin_action(
            actor="Super Admin",
            action_type="CREATE",
            domain="CampusSubscription",
            target_id=sub.subscription_id,
            description=f"Provisioned contract {sub.plan_name} for {school.name} (₹{contract_value:,.0f})"
        )
        return redirect('/super-admin/subscriptions/overview.html')

    return render(request, 'super-admin/subscriptions/create.html', {"schools": schools})


def payments_overview(request):
    """
    Super Admin: Consolidated Payments Ledger across subscriptions and recharges.
    """
    txns_qs = FinancialTransaction.objects.select_related('school', 'franchise', 'student').order_by('-created_at')
    settled_val = txns_qs.filter(status='Successful').aggregate(t=Sum('amount'))['t'] or 0
    pending_val = txns_qs.filter(status='Pending').aggregate(t=Sum('amount'))['t'] or 0
    failed_val = txns_qs.filter(status='Failed').aggregate(t=Sum('amount'))['t'] or 0
    refunded_val = txns_qs.filter(status='Refunded').aggregate(t=Sum('amount'))['t'] or 0
    settled_volume = f"₹{int(settled_val):,}" if settled_val > 0 else "₹0"
    pending_volume = f"₹{int(pending_val):,}" if pending_val > 0 else "₹0"
    failed_volume = f"₹{int(failed_val):,}" if failed_val > 0 else "₹0"
    refunded_volume = f"₹{int(refunded_val):,}" if refunded_val > 0 else "₹0" 

    payments_data = [
        {
            "id": t.transaction_id,
            "date": t.created_at.strftime("%Y-%m-%d %H:%M"),
            "entity": t.school.name if t.school else "Direct Payment",
            "franchise": t.franchise.name if t.franchise else (t.school.franchise.name if t.school and t.school.franchise else "Direct"),
            "category": t.category,
            "method": t.payment_method,
            "reference": t.gateway_reference or t.transaction_id,
            "amount": float(t.amount),
            "status": t.status
        }
        for t in txns_qs
    ]

    context = {
        "transactions": txns_qs,
        "payments_json": json.dumps(payments_data),
        "settled_volume": settled_volume,
        "pending_volume": pending_volume,
        "failed_volume": failed_volume,
        "refunded_volume": refunded_volume,
    }
    return render(request, 'super-admin/payments/overview.html', context)


def payment_details(request):
    """
    Super Admin: Official Payment Receipt & Tax Invoice Inspector.
    """
    txn_id = request.GET.get('id', '')
    txn = FinancialTransaction.objects.filter(transaction_id=txn_id).select_related('school', 'franchise', 'student').first()
    if not txn:
        txn = FinancialTransaction.objects.first()

    txn_dict = {
        "id": txn.transaction_id if txn else "TXN-98421",
        "date": txn.created_at.strftime("%Y-%m-%d %H:%M") if txn else "2026-11-10 14:22",
        "entity": txn.school.name if txn and txn.school else "Doon Valley Residential Academy",
        "franchise": txn.franchise.name if txn and txn.franchise else "North Telecom Franchise",
        "category": txn.category if txn else "Annual Subscription",
        "method": txn.payment_method if txn else "Razorpay / UPI",
        "reference": txn.gateway_reference if txn else "pay_L8x92KdN",
        "amount": float(txn.amount) if txn else 76560.00,
        "status": txn.status if txn else "Successful"
    }

    context = {
        "txn": txn,
        "txn_json": json.dumps(txn_dict),
    }
    return render(request, 'super-admin/payments/details.html', context)


# --- Call Logs & Reports ---

def call_history(request):
    """
    Super Admin: Fleet-wide Real-Time Call Telemetry Ledger.
    """
    calls_qs = CallRecord.objects.select_related('school', 'student').order_by('-start_time')[:250]

    call_history_data = [
        {
            "id": c.call_id,
            "studentName": c.student.name if c.student else "Student",
            "studentCode": c.student.calling_code if c.student else "",
            "school": c.school.name if c.school else "",
            "authorizedNumber": c.destination_number,
            "guardianName": c.call_type,
            "startTime": c.start_time.strftime("%Y-%m-%d %H:%M"),
            "dateOnly": c.start_time.strftime("%Y-%m-%d"),
            "duration": f"{c.duration_seconds // 60}m {c.duration_seconds % 60}s",
            "minutesUsed": c.minutes_deducted,
            "status": c.call_status
        }
        for c in calls_qs
    ]

    context = {
        "calls": calls_qs,
        "call_history_json": json.dumps(call_history_data),
    }
    return render(request, 'super-admin/call-history/index.html', context)


def reports_overview(request):
    """
    Super Admin: Multi-Campus Usage Analytics & Executive Report Generator.
    """
    schools_qs = School.objects.all().order_by('-enrolled_students')
    total_minutes = Student.objects.aggregate(t=Sum('remaining_minutes'))['t'] or 0
    total_students = Student.objects.count()
    active_students = Student.objects.filter(status='Active').count()
    inactive_students = Student.objects.filter(status__in=['Inactive', 'Suspended']).count()
    today = timezone.now().date()
    expiring_students = Student.objects.filter(status='Active', validity_expiry__lte=today + timedelta(days=14), validity_expiry__gte=today).count()

    school_usage_categories = []
    school_usage_data = []
    for s in schools_qs[:10]:
        mins = CallRecord.objects.filter(school=s).aggregate(m=Sum('minutes_deducted'))['m'] or 0
        school_usage_categories.append(s.name)
        school_usage_data.append(int(mins))

    has_usage_data = any(v > 0 for v in school_usage_data)
    student_health_data = [active_students, expiring_students, inactive_students] if total_students > 0 else []

    superadmin_charts = {
        "schoolUsage": {
            "categories": school_usage_categories if has_usage_data else [],
            "data": school_usage_data if has_usage_data else []
        },
        "studentStatus": {
            "categories": ['Active Accounts', 'Expiring <14d', 'Inactive / Expired'] if total_students > 0 else [],
            "data": student_health_data
        }
    }

    schools_data = [
        {
            "id": s.code,
            "code": s.code,
            "name": s.name,
            "city": s.city,
            "franchise": s.franchise.name if s.franchise else s.franchise_name_cache or "Unassigned",
            "adminName": s.admin_name,
            "adminEmail": s.admin_email,
            "students": s.students.count() or s.enrolled_students,
            "studentSeats": s.student_seats or 50,
            "activeStudents": s.students.filter(status='Active').count() or s.active_students,
            "subscriptionPlan": s.subscription_plan or "Enterprise Boarding",
            "subscriptionStatus": s.subscription_status or "Active",
            "status": s.status
        }
        for s in schools_qs
    ]

    context = {
        "schools": schools_qs,
        "schools_json": json.dumps(schools_data),
        "total_minutes": total_minutes,
        "total_students": total_students,
        "active_students": active_students,
        "superadmin_charts_json": json.dumps(superadmin_charts),
    }
    return render(request, 'super-admin/reports/index.html', context)


def export_reports_csv(request):
    """
    Super Admin: Export Executive CSV Performance Report.
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="super-admin-executive-report.csv"'

    writer = csv.writer(response)
    writer.writerow([
        "School Code", "Campus Name", "City", "Franchise Partner",
        "Enrolled Students", "Active Boarders", "Kiosk Devices", "Daily Duration Cap", "Subscription Status"
    ])

    for s in School.objects.select_related('franchise').all().order_by('code'):
        writer.writerow([
            s.code,
            s.name,
            s.city,
            s.franchise.name if s.franchise else "Direct",
            s.enrolled_students,
            s.active_students,
            s.device_count,
            s.daily_duration_cap,
            s.subscription_status
        ])

    return response


# --- Platform Settings ---

def settings_general(request):
    """
    Super Admin: Global Platform Governance & Operator Identity Settings.
    """
    settings = PlatformSetting.get_settings()
    if request.method == 'POST':
        settings.platform_title = request.POST.get('platform_name', settings.platform_title).strip()
        settings.support_email = request.POST.get('support_email', settings.support_email).strip()
        settings.save()

        log_admin_action(
            actor="Super Admin",
            action_type="UPDATE",
            domain="PlatformSettings",
            target_id="general",
            description="Updated global platform identity and support email"
        )
        return redirect('/super-admin/settings/general.html')

    return render(request, 'super-admin/settings/general.html', {"settings": settings})


def settings_notifications(request):
    """
    Super Admin: SMS Gateway Config & Notification Dispatch Matrix.
    """
    settings = PlatformSetting.get_settings()
    if request.method == 'POST':
        settings.sms_sender_id = request.POST.get('sms_sender_id', settings.sms_sender_id).strip()
        settings.low_balance_threshold_minutes = int(request.POST.get('threshold', settings.low_balance_threshold_minutes) or 15)
        settings.save()

        log_admin_action(
            actor="Super Admin",
            action_type="UPDATE",
            domain="Notifications",
            target_id="sms-gateway",
            description="Updated SMS Gateway dispatch templates and balance warning thresholds"
        )
        return redirect('/super-admin/settings/notifications.html')

    return render(request, 'super-admin/settings/notifications.html', {"settings": settings})


def settings_audit_logs(request):
    """
    Super Admin: Immutable Administrative Audit Log Ledger.
    """
    logs_qs = SystemAuditLog.objects.all().order_by('-timestamp')[:200]

    audit_logs_data = [
        {
            "timestamp": a.timestamp.strftime("%Y-%m-%d %H:%M"),
            "actor": a.actor,
            "module": a.target_domain,
            "action": a.description,
            "target": a.target_id,
            "ipAddress": a.ip_address or "127.0.0.1",
            "severity": "Critical" if a.action_type in ["POLICY_OVERRIDE", "TERMINAL_LOCKDOWN", "DELETE"] else ("Warning" if a.action_type == "UPDATE" else "Info")
        }
        for a in logs_qs
    ]

    context = {
        "audit_logs": logs_qs,
        "audit_logs_json": json.dumps(audit_logs_data),
    }
    return render(request, 'super-admin/settings/audit-logs.html', context)


def _parse_admin_post_data(request):
    data = {}
    if request.body:
        try:
            data = json.loads(request.body.decode('utf-8'))
        except Exception:
            pass
    if not data:
        data = request.POST.dict()
    return data


def school_toggle_status(request):
    """Super Admin: Toggle active/suspended status for single or batch schools."""
    if request.method != "POST":
        return JsonResponse({"error": "POST_REQUIRED", "message": "Method not allowed"}, status=405)
    data = _parse_admin_post_data(request)
    code = (data.get('school_code') or data.get('id') or data.get('code') or '').strip()
    ids = data.get('ids') or data.get('school_codes') or []
    target_status = (data.get('status') or 'Active').strip()
    if target_status not in ['Active', 'Suspended']:
        target_status = 'Active' if 'act' in target_status.lower() else 'Suspended'

    target_codes = []
    if isinstance(ids, list) and ids:
        target_codes = [str(x).strip() for x in ids if str(x).strip()]
    elif code:
        target_codes = [code]

    updated = School.objects.filter(code__in=target_codes).update(status=target_status)
    log_admin_action(
        actor=getattr(request.user, 'username', 'Super Admin'),
        action_type="UPDATE",
        domain="School Management",
        target_id=",".join(target_codes),
        description=f"Status set to {target_status} for {updated} school(s)."
    )
    return JsonResponse({
        "status": "success",
        "new_status": target_status,
        "count": updated,
        "message": f"Updated {updated} school(s) to {target_status}."
    })


def franchise_toggle_status(request):
    """Super Admin: Toggle active/suspended status for franchise partner."""
    if request.method != "POST":
        return JsonResponse({"error": "POST_REQUIRED"}, status=405)
    data = _parse_admin_post_data(request)
    target_id = (data.get('franchise_id') or data.get('id') or data.get('code') or '').strip()
    ids = data.get('ids') or []
    target_status = (data.get('status') or 'Active').strip()
    if target_status not in ['Active', 'Suspended']:
        target_status = 'Active' if 'act' in target_status.lower() else 'Suspended'

    targets = [str(x).strip() for x in ids if str(x).strip()] if ids else ([target_id] if target_id else [])
    qs = Franchise.objects.filter(Q(code__in=targets) | Q(id__in=[int(x) for x in targets if x.isdigit()]))
    updated = qs.update(status=target_status)
    log_admin_action(
        actor=getattr(request.user, 'username', 'Super Admin'),
        action_type="UPDATE",
        domain="Franchise Management",
        target_id=",".join(targets),
        description=f"Franchise partner status set to {target_status}."
    )
    return JsonResponse({
        "status": "success",
        "new_status": target_status,
        "count": updated
    })


def school_admin_toggle_status(request):
    """Super Admin: Deactivate or activate school administrator accounts."""
    if request.method != "POST":
        return JsonResponse({"error": "POST_REQUIRED"}, status=405)
    data = _parse_admin_post_data(request)
    target_id = (data.get('admin_id') or data.get('id') or '').strip()
    ids = data.get('ids') or []
    target_status = (data.get('status') or 'Active').strip()
    is_active = (target_status == 'Active')

    targets = [str(x).strip() for x in ids if str(x).strip()] if ids else ([target_id] if target_id else [])
    profiles = SchoolAdminProfile.objects.filter(Q(id__in=[int(x) for x in targets if x.isdigit()]) | Q(school__code__in=targets))
    for p in profiles:
        p.status = 'Active' if is_active else 'Inactive'
        p.save(update_fields=['status'])
        if p.user:
            p.user.is_active = is_active
            p.user.save(update_fields=['is_active'])

    users = User.objects.filter(Q(username__in=targets) | Q(email__in=targets) | Q(id__in=[int(x) for x in targets if x.isdigit()]))
    users.update(is_active=is_active)

    log_admin_action(
        actor=getattr(request.user, 'username', 'Super Admin'),
        action_type="UPDATE",
        domain="School Administrators",
        target_id=",".join(targets),
        description=f"Admin account active state set to {is_active}."
    )
    return JsonResponse({
        "status": "success",
        "new_status": 'Active' if is_active else 'Inactive',
        "is_active": is_active
    })


def subscription_renew(request):
    """Super Admin: Renew campus subscription term by +1 or more years."""
    if request.method != "POST":
        return JsonResponse({"error": "POST_REQUIRED"}, status=405)
    data = _parse_admin_post_data(request)
    target_id = (data.get('school_code') or data.get('id') or data.get('school') or '').strip()
    years = int(data.get('years') or 1)

    school = School.objects.filter(Q(code=target_id) | Q(name__icontains=target_id)).first()
    if not school:
        sub = CampusSubscription.objects.filter(id=int(target_id) if target_id.isdigit() else 0).first()
        if sub:
            school = sub.school

    new_expiry_date = timezone.now().date() + timedelta(days=365 * years)
    if school:
        school.status = 'Active'
        school.save(update_fields=['status'])

        sub, _ = CampusSubscription.objects.get_or_create(
            school=school,
            defaults={
                "subscription_id": f"SUB-{school.code}",
                "plan_name": getattr(school, 'subscription_plan', 'Enterprise Cloud') or "Enterprise Cloud",
                "expiry_date": new_expiry_date,
                "status": "Active"
            }
        )
        sub.expiry_date = new_expiry_date
        sub.status = "Active"
        sub.save(update_fields=['expiry_date', 'status'])

        log_admin_action(
            actor=getattr(request.user, 'username', 'Super Admin'),
            action_type="UPDATE",
            domain="Subscription Management",
            target_id=school.code,
            description=f"Subscription renewed for {years} year(s) through {new_expiry_date}."
        )

        return JsonResponse({
            "status": "success",
            "school": school.name,
            "expiry_date": new_expiry_date.strftime("%Y-%m-%d"),
            "new_status": "Active"
        })

    return JsonResponse({"error": "SCHOOL_NOT_FOUND", "message": "Target school or subscription not found."}, status=404)



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
