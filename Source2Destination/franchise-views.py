"""
Franchise Partner Views Implementation Source (franchise-views.py)
Source 2 Destination — Regional Operations Portal
Primary implementation source per AGENTS.md guidelines.
"""
import os
import io
import csv
import json
from datetime import datetime, date, timedelta
from django.shortcuts import render, redirect
from django.http import Http404, HttpResponseBadRequest, HttpResponse, JsonResponse
from django.template.loader import get_template
from django.template import TemplateDoesNotExist
from django.db.models import Sum, Count, Q
from django.utils import timezone
from django.contrib.auth.models import User
from .models import (
    School, Franchise, Student, AcademicClass, ClassSection,
    GlobalDurationRule, CampusDurationRule, CallingScheduleRule,
    RechargePlan, StudentRecharge, CallRecord, Guardian, SchoolAdminProfile
)
from .calling_services import (
    get_global_duration_rule, ValidityService, RechargeService
)


def get_current_franchise(request):
    """Retrieve the active franchise partner (defaults to FRN-101 North-East EduNet Partners)."""
    if getattr(request, 'user', None) and request.user.is_authenticated:
        if hasattr(request.user, 'franchise_partner') and request.user.franchise_partner:
            return request.user.franchise_partner
        fr = Franchise.objects.filter(user=request.user).first()
        if not fr and request.user.email:
            fr = Franchise.objects.filter(email__iexact=request.user.email).first()
        if fr:
            return fr

    code = request.GET.get('franchise_code') or request.session.get('franchise_code', 'FRN-101')
    franchise = Franchise.objects.filter(code=code).first()
    if not franchise:
        franchise = Franchise.objects.first()
    return franchise


def dashboard(request):
    """Render Franchise Partner Dashboard with live regional telemetry metrics."""
    franchise = get_current_franchise(request)
    schools_qs = School.objects.filter(franchise=franchise) if franchise else School.objects.none()
    total_campuses = schools_qs.count()
    active_campuses = schools_qs.filter(status='Active').count()
    students_qs = Student.objects.filter(school__franchise=franchise) if franchise else Student.objects.none()
    total_students = students_qs.count()
    active_students = students_qs.filter(status='Active').count()

    recent_schools = schools_qs.order_by('-id')[:5]
    recharges_qs = StudentRecharge.objects.filter(school__franchise=franchise).select_related('student', 'school', 'plan').order_by('-created_at') if franchise else StudentRecharge.objects.none()
    recent_recharges = recharges_qs[:5]

    comm_rate = float(franchise.commission_rate or 18.0) / 100.0 if franchise else 0.18
    successful_recharges = recharges_qs.filter(status='Successful')
    pending_recharges = recharges_qs.filter(status='Pending')

    earned_commission_val = float(successful_recharges.aggregate(total=Sum('amount'))['total'] or 0.0)
    earned_commission = earned_commission_val * comm_rate
    pending_commission_val = float(pending_recharges.aggregate(total=Sum('amount'))['total'] or 0.0)
    pending_commission = pending_commission_val * comm_rate

    calls_qs = CallRecord.objects.filter(school__franchise=franchise) if franchise else CallRecord.objects.none()
    calling_minutes = calls_qs.aggregate(total=Sum('minutes_deducted'))['total'] or 0

    # Build dynamic monthly categories and series for revenue & commission chart
    now = timezone.now()
    month_names = []
    gross_monthly = []
    comm_monthly = []
    for i in range(5, -1, -1):
        m_date = (now.replace(day=1) - timedelta(days=i * 28)).replace(day=1)
        m_name = m_date.strftime("%b")
        month_names.append(m_name)
        m_recharges = successful_recharges.filter(created_at__year=m_date.year, created_at__month=m_date.month)
        m_gross = float(m_recharges.aggregate(s=Sum('amount'))['s'] or 0.0)
        gross_monthly.append(round(m_gross, 2))
        comm_monthly.append(round(m_gross * comm_rate, 2))

    # School students distribution
    school_names = []
    school_student_counts = []
    for s in schools_qs[:5]:
        s_count = Student.objects.filter(school=s).count()
        school_names.append(s.name[:18])
        school_student_counts.append(s_count)

    franchise_charts = {
        "revenue": {
            "categories": month_names,
            "gross": gross_monthly,
            "commission": comm_monthly
        },
        "schoolStudents": {
            "categories": school_names,
            "data": school_student_counts
        }
    }

    context = {
        "franchise": franchise,
        "total_campuses": total_campuses,
        "active_campuses": active_campuses,
        "total_students": total_students,
        "active_students": active_students,
        "recent_schools": recent_schools,
        "recent_recharges": recent_recharges,
        "earned_commission": f"{earned_commission:,.2f}",
        "pending_commission": f"{pending_commission:,.2f}",
        "calling_minutes": f"{calling_minutes:,}",
        "franchise_charts_json": json.dumps(franchise_charts),
    }
    return render(request, 'franchise/dashboard.html', context)


def schools_list(request):
    """Dynamic franchise assigned schools list view."""
    franchise = get_current_franchise(request)
    schools_qs = School.objects.filter(franchise=franchise).order_by('-id')
    total_campuses = schools_qs.count()
    active_campuses = schools_qs.filter(status='Active').count()
    total_students = Student.objects.filter(school__franchise=franchise).count()

    schools_data = [
        {
            "id": s.code,
            "code": s.code,
            "name": s.name,
            "city": s.city,
            "franchiseId": s.franchise.code if s.franchise else "",
            "franchise": s.franchise.name if s.franchise else "",
            "adminName": s.admin_name,
            "adminEmail": s.admin_email,
            "students": Student.objects.filter(school=s).count() or s.enrolled_students,
            "studentSeats": s.student_seats,
            "activeStudents": Student.objects.filter(school=s, status='Active').count() or s.active_students,
            "callingMinutes": Student.objects.filter(school=s, status='Active').count() * 45,
            "subscriptionPlan": s.subscription_plan,
            "subscriptionStatus": s.subscription_status,
            "status": s.status
        }
        for s in schools_qs
    ]

    context = {
        "franchise": franchise,
        "schools": schools_qs,
        "schools_json": json.dumps(schools_data),
        "total_campuses": total_campuses,
        "active_campuses": active_campuses,
        "total_students": total_students,
    }
    return render(request, 'franchise/schools/list.html', context)


def school_add(request):
    """Franchise: Onboard an assigned school under current territory."""
    franchise = get_current_franchise(request)

    if request.method == "POST":
        name = request.POST.get('name', '').strip()
        city = request.POST.get('city', '').strip()
        if not name or not city:
            return HttpResponseBadRequest("Name and City are required fields.")

        code = request.POST.get('code', '').strip()
        if not code:
            code = f"SCH-{School.objects.count() + 1001}"
        elif School.objects.filter(code=code).exists():
            code = f"{code}-{School.objects.count() + 1}"

        seats = int(request.POST.get('students') or request.POST.get('student_seats') or 400)
        daily_cap = int(request.POST.get('daily_duration_cap') or 15)

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
            hostel_blocks_count=int(request.POST.get('hostel_blocks_count') or 3),
            franchise=franchise,
            franchise_name_cache=franchise.name if franchise else '',
            admin_name=request.POST.get('admin_name', 'Campus Administrator'),
            admin_email=request.POST.get('adminEmail') or request.POST.get('admin_email') or 'admin@institution.edu',
            admin_phone=request.POST.get('phone') or request.POST.get('admin_phone') or '',
            secondary_contact_name=request.POST.get('secondary_contact_name', ''),
            secondary_contact_email=request.POST.get('secondary_contact_email', ''),
            secondary_contact_phone=request.POST.get('secondary_contact_phone', ''),
            daily_duration_cap=daily_cap,
            allowed_calling_days=request.POST.get('allowed_calling_days', 'All 7 Days'),
            emergency_calling_allowed=True,
            subscription_plan=request.POST.get('subscription_plan', 'Campus Growth Annual'),
            billing_cycle=request.POST.get('billing_cycle', 'Annually'),
            student_seats=seats,
            enrolled_students=seats,
            active_students=seats,
            status='Active',
            subscription_status="Active"
        )

        # Create or update School Administrator login credentials
        admin_username = request.POST.get('username', '').strip()
        admin_password = request.POST.get('password', '').strip() or '12345'
        admin_email = request.POST.get('adminEmail') or request.POST.get('admin_email') or f"admin@{code.lower()}.edu"
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
                "phone": request.POST.get('phone') or request.POST.get('admin_phone') or '',
                "designation": "Campus Principal / Administrator",
                "status": "Active"
            }
        )

        return redirect('/franchise/schools/list.html')

    context = {
        "franchise": franchise,
    }
    return render(request, 'franchise/schools/add.html', context)


def school_details(request):
    """Franchise: School detail 360 view."""
    school_id = request.GET.get('id')
    school = School.objects.filter(Q(code=school_id) | Q(id=school_id if str(school_id).isdigit() else 0)).first()
    if not school:
        school = School.objects.first()

    franchise = school.franchise if school else get_current_franchise(request)
    students_qs = Student.objects.filter(school=school).order_by('-id') if school else Student.objects.none()
    recharges_qs = StudentRecharge.objects.filter(school=school).select_related('student', 'plan').order_by('-created_at') if school else StudentRecharge.objects.none()

    students_data = [
        {
            "id": s.code,
            "code": s.code,
            "studentCode": s.calling_code,
            "name": s.name,
            "gender": s.gender,
            "schoolId": s.school.code,
            "school": s.school.name,
            "franchiseId": franchise.code if franchise else "",
            "className": s.class_name,
            "section": s.section,
            "primaryPhone": s.primary_phone,
            "guardianName": s.guardian_name,
            "remainingMinutes": s.remaining_minutes,
            "status": s.status
        }
        for s in students_qs
    ]

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
        "school": school,
        "franchise": franchise,
        "students": students_qs[:20],
        "students_json": json.dumps(students_data),
        "recharges_json": json.dumps(recharges_data),
    }
    return render(request, 'franchise/schools/details.html', context)


def school_edit(request):
    """Franchise: Edit assigned school information."""
    school_id = request.GET.get('id')
    school = School.objects.filter(Q(code=school_id) | Q(id=school_id if str(school_id).isdigit() else 0)).first()
    if not school:
        school = School.objects.first()

    if request.method == "POST" and school:
        school.name = request.POST.get('name', school.name).strip()
        school.city = request.POST.get('city', school.city).strip()
        if request.POST.get('state'):
            school.state = request.POST.get('state').strip()
        if request.POST.get('address'):
            school.address = request.POST.get('address').strip()
        if request.POST.get('postal_code'):
            school.postal_code = request.POST.get('postal_code').strip()

        school.admin_name = (request.POST.get('admin_name') or request.POST.get('adminName', school.admin_name)).strip()
        # Note: admin_email and admin_phone are locked and cannot be changed by Franchise Admin

        if request.POST.get('secondary_contact_name'):
            school.secondary_contact_name = request.POST.get('secondary_contact_name').strip()
        if request.POST.get('secondary_contact_phone'):
            school.secondary_contact_phone = request.POST.get('secondary_contact_phone').strip()

        if request.POST.get('daily_duration_cap'):
            try:
                school.daily_duration_cap = int(request.POST['daily_duration_cap'])
            except ValueError:
                pass

        if 'emergency_calling_allowed' in request.POST:
            school.emergency_calling_allowed = request.POST.get('emergency_calling_allowed') in ['true', 'True', '1', 'on']
        if request.POST.get('kiosk_group_tag'):
            school.kiosk_group_tag = request.POST.get('kiosk_group_tag').strip()
        if request.POST.get('students') or request.POST.get('student_seats'):
            try:
                seats = int(request.POST.get('students') or request.POST.get('student_seats'))
                school.student_seats = seats
                school.enrolled_students = seats
            except (ValueError, TypeError):
                pass

        school.save()
        return redirect(f"/franchise/schools/details.html?id={school.code}")

    context = {
        "school": school,
        "franchise": school.franchise if school else get_current_franchise(request)
    }
    return render(request, 'franchise/schools/edit.html', context)


def students_list(request):
    """Dynamic franchise student directory view."""
    franchise = get_current_franchise(request)
    students_qs = Student.objects.filter(school__franchise=franchise).select_related('school').order_by('-id')
    total_students = students_qs.count()
    active_students = students_qs.filter(status='Active').count()

    students_data = [
        {
            "id": s.code,
            "code": s.code,
            "studentCode": s.calling_code,
            "name": s.name,
            "gender": s.gender,
            "schoolId": s.school.code,
            "school": s.school.name,
            "franchiseId": franchise.code,
            "className": s.class_name,
            "section": s.section,
            "primaryPhone": s.primary_phone,
            "guardianName": s.guardian_name,
            "remainingMinutes": s.remaining_minutes,
            "status": s.status
        }
        for s in students_qs
    ]

    context = {
        "franchise": franchise,
        "students": students_qs,
        "students_json": json.dumps(students_data),
        "total_students": total_students,
        "active_students": active_students,
    }
    return render(request, 'franchise/students/list.html', context)


def student_details(request):
    """Franchise: Student profile details view."""
    student_id = request.GET.get('id')
    stu = Student.objects.filter(Q(code=student_id) | Q(id=student_id if str(student_id).isdigit() else 0)).select_related('school').first()
    if not stu:
        stu = Student.objects.first()

    calls_qs = CallRecord.objects.filter(student=stu).select_related('guardian', 'school').order_by('-start_time') if stu else CallRecord.objects.none()
    call_records_data = [
        {
            "id": c.call_id,
            "studentName": c.student.name if c.student else "Student",
            "studentCode": c.student.calling_code if c.student else "N/A",
            "school": c.school.name,
            "authorizedNumber": c.destination_number,
            "guardianName": c.guardian.name if c.guardian else c.call_type,
            "startTime": c.start_time.strftime("%Y-%m-%d %H:%M"),
            "duration": f"{c.duration_seconds // 60}m {c.duration_seconds % 60:02d}s" if c.duration_seconds > 0 else "0m 00s",
            "minutesUsed": c.minutes_deducted,
            "status": c.call_status,
            "dateOnly": c.start_time.strftime("%Y-%m-%d"),
            "recordingUrl": c.audio_recording_url,
        }
        for c in calls_qs[:50]
    ]

    context = {
        "student": stu,
        "school": stu.school if stu else None,
        "franchise": stu.school.franchise if stu and stu.school else get_current_franchise(request),
        "calls": calls_qs[:50],
        "call_history_json": json.dumps(call_records_data),
    }
    return render(request, 'franchise/students/details.html', context)


def student_edit(request):
    """Franchise: Edit student calling profile and guardian contact numbers."""
    student_id = request.GET.get('id')
    stu = Student.objects.filter(Q(code=student_id) | Q(id=student_id if str(student_id).isdigit() else 0)).select_related('school').first()
    if not stu:
        stu = Student.objects.first()

    if request.method == "POST" and stu:
        stu.name = request.POST.get('name', stu.name).strip()
        stu.class_name = request.POST.get('className', stu.class_name).strip()
        stu.section = request.POST.get('section', stu.section).strip()
        stu.primary_phone = (request.POST.get('primaryPhone') or request.POST.get('primary_phone', stu.primary_phone)).strip()
        stu.secondary_phone = (request.POST.get('secondaryPhone') or request.POST.get('secondary_phone', stu.secondary_phone)).strip()
        if 'guardianName' in request.POST or 'guardian_name' in request.POST:
            stu.guardian_name = (request.POST.get('guardianName') or request.POST.get('guardian_name', stu.guardian_name)).strip()
        if 'pin' in request.POST and request.POST['pin'].strip():
            stu.pin = request.POST['pin'].strip()
        if 'wallet_balance' in request.POST:
            try:
                stu.wallet_balance = float(request.POST['wallet_balance'])
            except (ValueError, TypeError):
                pass
        if 'date_of_birth' in request.POST and request.POST['date_of_birth']:
            try:
                stu.date_of_birth = datetime.strptime(request.POST['date_of_birth'], "%Y-%m-%d").date()
            except ValueError:
                pass
        if 'status' in request.POST:
            stu.status = request.POST['status']
        stu.save()
        return redirect(f"/franchise/students/details.html?id={stu.code}")

    context = {
        "student": stu,
        "school": stu.school if stu else None,
        "franchise": stu.school.franchise if stu and stu.school else get_current_franchise(request),
    }
    return render(request, 'franchise/students/edit.html', context)


def student_add(request):
    """Franchise: Enroll new student under assigned franchise schools."""
    franchise = get_current_franchise(request)
    schools = School.objects.filter(franchise=franchise).order_by('name')

    if request.method == "POST":
        school_code = request.POST.get('school')
        school = School.objects.filter(code=school_code, franchise=franchise).first() or schools.first()
        name = request.POST.get('name', '').strip()
        if not name:
            return HttpResponseBadRequest("Student name is required.")

        code = f"STU-{Student.objects.count() + 4001}"
        calling_code = f"S2D-{school.code[:3] if school else 'SCH'}-{Student.objects.count() + 8801}"

        dob = None
        if request.POST.get('date_of_birth'):
            try:
                dob = datetime.strptime(request.POST['date_of_birth'], "%Y-%m-%d").date()
            except ValueError:
                pass

        Student.objects.create(
            code=code,
            calling_code=calling_code,
            name=name,
            gender=request.POST.get('gender', 'Male'),
            school=school,
            class_name=request.POST.get('className', 'Grade 10'),
            section=request.POST.get('section', 'Section A'),
            guardian_name=request.POST.get('guardianName') or request.POST.get('guardian_name') or 'Authorized Guardian',
            primary_phone=request.POST.get('primaryPhone') or request.POST.get('primary_phone', ''),
            secondary_phone=request.POST.get('secondaryPhone') or request.POST.get('secondary_phone', ''),
            pin=request.POST.get('pin', '1234'),
            date_of_birth=dob,
            wallet_balance=float(request.POST.get('wallet_balance') or 50.00),
            remaining_minutes=int(request.POST.get('remaining_minutes') or 120),
            daily_limit_min=school.daily_duration_cap if school else 15,
            status=request.POST.get('status', 'Active')
        )
        return redirect('/franchise/students/list.html')

    context = {
        "franchise": franchise,
        "schools": schools,
    }
    return render(request, 'franchise/students/add.html', context)


def classes_list(request):
    """Dynamic Franchise Assigned-School Classes & Sections view."""
    franchise = get_current_franchise(request)
    schools = School.objects.filter(franchise=franchise).order_by('name')

    if request.method == "POST":
        school_id = request.POST.get('school_id')
        school = School.objects.filter(Q(code=school_id) | Q(name__icontains=school_id), franchise=franchise).first()
        if not school:
            school = schools.first()

        class_name = (request.POST.get('class_name') or request.POST.get('className') or '').strip()
        sections_str = (request.POST.get('sections') or 'Section A').strip()

        if school and class_name:
            digits = ''.join(c for c in class_name if c.isdigit())
            code = f"CLS-{digits}" if digits else f"CLS-{AcademicClass.objects.filter(school=school).count() + 1:02d}"

            cls_obj, _ = AcademicClass.objects.get_or_create(
                school=school,
                name=class_name,
                defaults={
                    "code": code,
                    "supervisor": school.admin_name or "Faculty Coordinator",
                    "default_daily_minutes": school.daily_duration_cap or 15,
                    "schedule_group": "Standard Hostel Window",
                    "status": "Active"
                }
            )

            # Create sections from comma-separated string
            sec_names = [s.strip() for s in sections_str.split(',') if s.strip()]
            for sec_name in sec_names:
                sec_letter = ''.join(c for c in sec_name if c.isalpha())
                sec_code = f"SEC-{digits}{sec_letter[:1]}" if (digits and sec_letter) else f"SEC-{ClassSection.objects.filter(school=school).count() + 1:02d}"
                ClassSection.objects.get_or_create(
                    academic_class=cls_obj,
                    name=sec_name,
                    defaults={
                        "school": school,
                        "code": sec_code,
                        "room_wing": "Campus Boarding Wing",
                        "advisor": cls_obj.supervisor,
                        "assigned_booth": "Main Campus Booth 1",
                        "status": "Active"
                    }
                )

        return redirect('/franchise/classes/index.html')

    # Query all classes for the franchise's schools
    classes_qs = AcademicClass.objects.filter(school__franchise=franchise, status='Active').select_related('school').order_by('school__name', 'name')

    classes_data = [
        {
            "id": c.code,
            "className": f"{c.school.name} — {c.name}" if schools.count() > 1 else c.name,
            "supervisor": c.supervisor or "Faculty Coordinator",
            "sectionsCount": c.sections.filter(status='Active').count(),
            "studentsCount": Student.objects.filter(school=c.school, class_name__iexact=c.name).count(),
            "activeAccounts": Student.objects.filter(school=c.school, class_name__iexact=c.name, status='Active').count(),
            "defaultDailyMinutes": c.default_daily_minutes,
            "scheduleGroup": c.schedule_group,
            "status": c.status
        }
        for c in classes_qs
    ]

    context = {
        "franchise": franchise,
        "schools": schools,
        "classes": classes_qs,
        "classes_json": json.dumps(classes_data),
        "total_classes": classes_qs.count(),
    }
    return render(request, 'franchise/classes/index.html', context)


def calling_duration(request):
    """Franchise: Configure territory calling duration limits within inherited Super Admin ceilings."""
    franchise = get_current_franchise(request)
    schools = School.objects.filter(franchise=franchise).order_by('name')
    global_rule = get_global_duration_rule()

    if request.method == "POST":
        target_school = request.POST.get('target_school')
        per_call_limit = min(global_rule.hard_max_call_duration, int(request.POST.get('per_call_limit', 15)))
        daily_limit = min(global_rule.max_daily_student_cap, int(request.POST.get('daily_limit', 20)))

        if target_school and target_school != "All Assigned Schools (Territory Default)":
            sch = School.objects.filter(code=target_school, franchise=franchise).first() or School.objects.filter(name=target_school, franchise=franchise).first()
            if sch:
                sch.daily_duration_cap = daily_limit
                sch.save(update_fields=['daily_duration_cap'])
                rule, _ = CampusDurationRule.objects.get_or_create(school=sch, scope="School-Wide Default")
                rule.max_call_duration = per_call_limit
                rule.daily_cumulative_limit = daily_limit
                rule.save()
        else:
            for sch in schools:
                sch.daily_duration_cap = daily_limit
                sch.save(update_fields=['daily_duration_cap'])
                rule, _ = CampusDurationRule.objects.get_or_create(school=sch, scope="School-Wide Default")
                rule.max_call_duration = per_call_limit
                rule.daily_cumulative_limit = daily_limit
                rule.save()

        return redirect('/franchise/calling-duration/index.html')

    context = {
        "franchise": franchise,
        "schools": schools,
        "global_rule": global_rule,
    }
    return render(request, 'franchise/calling-duration/index.html', context)


def calling_schedules(request):
    """Franchise: Assigned-school calling schedule management."""
    franchise = get_current_franchise(request)
    schools = School.objects.filter(franchise=franchise).order_by('name')
    first_school = schools.first()
    schedules = CallingScheduleRule.objects.filter(
        Q(school__in=schools) | Q(school__isnull=True),
        is_active=True
    ).order_by('start_time')

    context = {
        "franchise": franchise,
        "schools": schools,
        "first_school": first_school,
        "schedules": schedules,
    }
    return render(request, 'franchise/calling-schedules/index.html', context)


def validity_overview(request):
    """Franchise: Territory student calling validity management."""
    franchise = get_current_franchise(request)
    students_qs = Student.objects.filter(school__franchise=franchise).select_related('school').order_by('-id')

    students_data = [
        {
            "id": s.code,
            "name": s.name,
            "studentCode": s.calling_code,
            "school": s.school.name,
            "validityStart": s.validity_start.strftime("%Y-%m-%d") if s.validity_start else "-",
            "validityExpiry": s.validity_expiry.strftime("%Y-%m-%d") if s.validity_expiry else "-",
            "remainingMinutes": s.remaining_minutes,
            "validityStatus": ValidityService.evaluate(s)["status"],
            "status": s.status,
        }
        for s in students_qs
    ]

    context = {
        "franchise": franchise,
        "students": students_qs,
        "students_json": json.dumps(students_data),
    }
    return render(request, 'franchise/validity/index.html', context)


def recharges_overview(request):
    """Franchise: Territory recharge requests and credit allocations."""
    franchise = get_current_franchise(request)
    recharges_qs = StudentRecharge.objects.filter(school__franchise=franchise).select_related('student', 'school').order_by('-created_at')

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
        "franchise": franchise,
        "recharges": recharges_qs,
        "recharges_json": json.dumps(recharges_data),
    }
    return render(request, 'franchise/recharges/index.html', context)


def commissions_overview(request):
    """Dynamic Franchise Territory Revenue & Commission Management Ledger."""
    franchise = get_current_franchise(request)
    recharges_qs = StudentRecharge.objects.filter(school__franchise=franchise).select_related('school', 'student', 'plan').order_by('-created_at')

    comm_rate = float(franchise.commission_rate or 18.0) / 100.0 if franchise else 0.18
    successful_recharges = recharges_qs.filter(status='Successful')
    pending_recharges = recharges_qs.filter(status='Pending')

    total_revenue = float(successful_recharges.aggregate(total=Sum('amount'))['total'] or 0.0)
    earned_commission = total_revenue * comm_rate
    pending_revenue = float(pending_recharges.aggregate(total=Sum('amount'))['total'] or 0.0)
    pending_commission = pending_revenue * comm_rate

    commissions_data = [
        {
            "id": f"COM-{r.recharge_id}" if r.recharge_id else f"COM-{r.id}",
            "period": r.created_at.strftime("%b %Y"),
            "school": r.school.name,
            "sourceType": r.plan_name_cache or "Prepaid Calling Pack",
            "grossAmount": float(r.amount),
            "commissionEarned": round(float(r.amount) * comm_rate, 2),
            "rate": f"{franchise.commission_rate}%" if franchise else "18%",
            "status": "Successful" if r.status == 'Successful' else "Pending",
            "payoutDate": (r.created_at + timedelta(days=5)).strftime("%Y-%m-%d"),
        }
        for r in recharges_qs
    ]

    # Chart data for monthly revenue and settled vs pending
    now = timezone.now()
    month_names = []
    gross_monthly = []
    comm_monthly = []
    settled_monthly = []
    pending_monthly = []
    has_comm_data = False
    for i in range(5, -1, -1):
        m_date = (now.replace(day=1) - timedelta(days=i * 28)).replace(day=1)
        m_name = m_date.strftime("%b")
        month_names.append(m_name)
        m_succ = successful_recharges.filter(created_at__year=m_date.year, created_at__month=m_date.month)
        m_pend = pending_recharges.filter(created_at__year=m_date.year, created_at__month=m_date.month)
        s_val = float(m_succ.aggregate(s=Sum('amount'))['s'] or 0.0) * comm_rate
        p_val = float(m_pend.aggregate(s=Sum('amount'))['s'] or 0.0) * comm_rate
        settled_monthly.append(round(s_val, 2))
        pending_monthly.append(round(p_val, 2))
        g_val = s_val / comm_rate if comm_rate > 0 else 0
        gross_monthly.append(round(g_val, 2))
        comm_monthly.append(round(s_val, 2))
        if s_val > 0 or p_val > 0:
            has_comm_data = True

    franchise_charts = {
        "revenue": {
            "categories": month_names if has_comm_data else [],
            "gross": gross_monthly if has_comm_data else [],
            "commission": comm_monthly if has_comm_data else []
        },
        "commissionBar": {
            "categories": month_names if has_comm_data else [],
            "settled": settled_monthly if has_comm_data else [],
            "pending": pending_monthly if has_comm_data else []
        }
    }

    context = {
        "franchise": franchise,
        "total_revenue": total_revenue,
        "earned_commission": earned_commission,
        "pending_commission": pending_commission,
        "commissions_json": json.dumps(commissions_data),
        "franchise_charts_json": json.dumps(franchise_charts),
    }
    return render(request, 'franchise/commissions/index.html', context)


def transactions_overview(request):
    """Dynamic Franchise Payment & Transaction History."""
    franchise = get_current_franchise(request)
    recharges_qs = StudentRecharge.objects.filter(school__franchise=franchise).select_related('school', 'student', 'plan').order_by('-created_at')

    transactions_data = [
        {
            "id": r.recharge_id,
            "date": r.created_at.strftime("%Y-%m-%d %H:%M"),
            "entity": r.school.name,
            "franchise": franchise.name if franchise else "Regional Partner",
            "category": "Student Recharge",
            "method": r.payment_mode or "Campus Desk",
            "reference": r.voucher_ref or f"REF-{r.id:06d}",
            "amount": float(r.amount),
            "status": r.status,
        }
        for r in recharges_qs
    ]

    total_count = recharges_qs.count()
    successful_count = recharges_qs.filter(status='Successful').count()
    total_volume = float(recharges_qs.aggregate(s=Sum('amount'))['s'] or 0.0)

    context = {
        "franchise": franchise,
        "recharges": recharges_qs,
        "transactions_json": json.dumps(transactions_data),
        "total_count": total_count,
        "successful_count": successful_count,
        "total_volume": total_volume,
    }
    return render(request, 'franchise/transactions/index.html', context)


def call_history(request):
    """Dynamic Regional Multi-School Call History & Telemetry Log."""
    franchise = get_current_franchise(request)
    schools_qs = School.objects.filter(franchise=franchise)
    calls_qs = CallRecord.objects.filter(school__in=schools_qs).select_related('student', 'school', 'guardian').order_by('-start_time')

    q = request.GET.get('q', '').strip()
    if q:
        calls_qs = calls_qs.filter(
            Q(call_id__icontains=q) |
            Q(student__name__icontains=q) |
            Q(student__calling_code__icontains=q) |
            Q(destination_number__icontains=q) |
            Q(school__name__icontains=q)
        )

    status_filter = request.GET.get('status', '').strip()
    if status_filter:
        calls_qs = calls_qs.filter(call_status=status_filter)

    school_filter = request.GET.get('school', '').strip()
    if school_filter:
        calls_qs = calls_qs.filter(Q(school__code=school_filter) | Q(school__name__icontains=school_filter))

    total_calls = calls_qs.count()
    completed_calls = calls_qs.filter(call_status='Completed').count()
    restricted_calls = calls_qs.filter(call_status='Restricted Schedule').count()
    total_minutes = calls_qs.aggregate(total=Sum('minutes_deducted'))['total'] or 0

    call_history_data = [
        {
            "id": c.call_id,
            "studentName": c.student.name if c.student else "Student",
            "studentCode": c.student.calling_code if c.student else "N/A",
            "school": c.school.name,
            "authorizedNumber": c.destination_number,
            "guardianName": c.guardian.name if c.guardian else c.call_type,
            "startTime": c.start_time.strftime("%Y-%m-%d %H:%M"),
            "duration": f"{c.duration_seconds // 60}m {c.duration_seconds % 60:02d}s" if c.duration_seconds > 0 else "0m 00s",
            "minutesUsed": c.minutes_deducted,
            "status": c.call_status,
            "dateOnly": c.start_time.strftime("%Y-%m-%d"),
            "recordingUrl": c.audio_recording_url,
        }
        for c in calls_qs[:200]
    ]

    context = {
        "franchise": franchise,
        "schools": schools_qs,
        "calls": calls_qs[:200],
        "call_history_json": json.dumps(call_history_data),
        "total_calls": total_calls,
        "completed_calls": completed_calls,
        "restricted_calls": restricted_calls,
        "total_minutes": total_minutes,
    }
    return render(request, 'franchise/call-history/index.html', context)


def bulk_upload(request):
    """Dynamic Franchise Multi-School Student Bulk CSV / Excel Upload."""
    franchise = get_current_franchise(request)
    schools = School.objects.filter(franchise=franchise).order_by('name')
    upload_result = None

    if request.method == "POST" and (request.FILES.get('spreadsheet') or request.FILES.get('file')):
        uploaded_file = request.FILES.get('spreadsheet') or request.FILES.get('file')
        filename = uploaded_file.name
        school_param = request.POST.get('school_id') or request.POST.get('school')
        default_school = School.objects.filter(Q(code=school_param) | Q(name=school_param), franchise=franchise).first() or schools.first()

        try:
            decoded_file = uploaded_file.read().decode('utf-8-sig')
            reader = csv.DictReader(io.StringIO(decoded_file))

            valid_rows = []
            error_rows = []
            row_idx = 1

            for row in reader:
                row_idx += 1
                name = (row.get('student_full_name') or row.get('Name') or row.get('student_name') or '').strip()
                class_name = (row.get('class_grade') or row.get('Class') or 'Grade 10').strip()
                section = (row.get('section') or row.get('Section') or 'Section A').strip()
                phone = (row.get('father_authorized_phone') or row.get('Primary Phone') or row.get('primary_phone') or '').strip()
                guardian = (row.get('guardian_name') or row.get('Guardian') or 'Authorized Guardian').strip()
                gender = (row.get('gender') or 'Male').strip()
                minutes = int(row.get('allocated_minutes') or 120)
                pin = (row.get('pin') or '1234').strip()
                dob_str = (row.get('date_of_birth') or '').strip()
                dob = None
                if dob_str:
                    try:
                        dob = datetime.strptime(dob_str, "%Y-%m-%d").date()
                    except ValueError:
                        pass

                row_school_code = (row.get('school_code') or row.get('school') or '').strip()
                target_school = default_school
                if row_school_code:
                    s_cand = School.objects.filter(Q(code=row_school_code) | Q(name__icontains=row_school_code), franchise=franchise).first()
                    if s_cand:
                        target_school = s_cand

                if not target_school:
                    error_rows.append({"row": row_idx, "name": name, "reason": "No valid assigned school selected or specified"})
                    continue

                if not name:
                    error_rows.append({"row": row_idx, "name": name, "reason": "Missing mandatory student name"})
                    continue
                if not phone:
                    error_rows.append({"row": row_idx, "name": name, "reason": "Missing mandatory authorized phone"})
                    continue

                if Student.objects.filter(school=target_school, primary_phone=phone).exists():
                    error_rows.append({
                        "row": row_idx,
                        "name": name,
                        "reason": f"Duplicate student phone '{phone}' already enrolled at {target_school.name}"
                    })
                    continue

                new_count = Student.objects.count() + 1
                calling_code = f"S2D-{target_school.code[:3] if target_school else 'SCH'}-{new_count + 8800}"
                stu_code = f"STU-{new_count + 4000}"

                Student.objects.create(
                    code=stu_code,
                    calling_code=calling_code,
                    name=name,
                    gender=gender,
                    school=target_school,
                    class_name=class_name,
                    section=section,
                    primary_phone=phone,
                    guardian_name=guardian,
                    pin=pin,
                    date_of_birth=dob,
                    wallet_balance=50.00,
                    remaining_minutes=minutes,
                    daily_limit_min=target_school.daily_duration_cap if target_school else 15,
                    status='Active'
                )

                valid_rows.append({
                    "row": row_idx,
                    "name": name,
                    "class_name": f"{class_name} · {section}",
                    "school": target_school.name,
                    "phone": phone,
                    "status": "Imported",
                    "code": calling_code
                })

            upload_result = {
                "filename": filename,
                "total_processed": row_idx - 1,
                "valid_count": len(valid_rows),
                "error_count": len(error_rows),
                "valid_rows": valid_rows,
                "error_rows": error_rows,
                "success": len(valid_rows) > 0,
            }

            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('format') == 'json':
                return JsonResponse(upload_result)

        except Exception as e:
            upload_result = {
                "filename": filename,
                "error": f"Failed to parse spreadsheet: {str(e)}",
                "valid_count": 0,
                "error_count": 1,
                "valid_rows": [],
                "error_rows": [{"row": "-", "name": "-", "reason": str(e)}],
                "success": False
            }

    context = {
        "franchise": franchise,
        "schools": schools,
        "upload_result": upload_result,
    }
    return render(request, 'franchise/bulk-upload/index.html', context)


def download_sample_csv(request):
    """Generate official S2D Student Enrollment bulk import CSV template for franchise."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="s2d_franchise_student_upload_sample.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'student_full_name',
        'class_grade',
        'section',
        'father_authorized_phone',
        'guardian_name',
        'gender',
        'hostel_wing',
        'allocated_minutes',
        'date_of_birth',
        'pin',
        'school_code'
    ])
    writer.writerow(['Aarav Sharma', 'Grade 10', 'Section A', '+919810123456', 'Rajesh Sharma', 'Male', 'Tagore Bhavan Rm 101', '120', '2010-04-15', '1234', 'SCH-1001'])
    writer.writerow(['Diya Patel', 'Grade 11', 'Section B', '+919820234567', 'Kiran Patel', 'Female', 'Sarojini House Rm 204', '150', '2009-08-22', '5678', 'SCH-1001'])
    writer.writerow(['Rohan Mukherjee', 'Grade 9', 'Section C', '+919830345678', 'Anirban Mukherjee', 'Male', 'Raman Wing Rm 312', '90', '2011-01-10', '9012', 'SCH-1001'])
    return response


def reports_overview(request):
    """Dynamic Franchise Territory School-wise & Student-wise Analytics & Reports."""
    franchise = get_current_franchise(request)
    schools_qs = School.objects.filter(franchise=franchise).order_by('name')

    schools_data = []
    school_names = []
    school_students = []
    total_minutes = 0

    for s in schools_qs:
        s_students = Student.objects.filter(school=s).count() or s.enrolled_students or s.student_seats or 0
        s_active = Student.objects.filter(school=s, status='Active').count() or s.active_students or 0
        s_minutes = s.call_records.aggregate(m=Sum('minutes_deducted'))['m'] or (s_active * 45)
        total_minutes += s_minutes
        school_names.append(s.name[:18])
        school_students.append(s_students)

        schools_data.append({
            "id": s.code,
            "code": s.code,
            "name": s.name,
            "city": s.city,
            "franchiseId": franchise.code if franchise else "",
            "franchise": franchise.name if franchise else "",
            "adminName": s.admin_name,
            "adminEmail": s.admin_email,
            "students": s_students,
            "studentSeats": s.student_seats,
            "activeStudents": s_active,
            "callingMinutes": s_minutes,
            "subscriptionPlan": s.subscription_plan,
            "subscriptionStatus": s.subscription_status,
            "status": s.status
        })

    # Weekly Calling minutes (last 8 weeks)
    now = timezone.now()
    week_cats = []
    week_data = []
    has_week_data = False
    calls_qs = CallRecord.objects.filter(school__in=schools_qs)
    for i in range(7, -1, -1):
        w_start = now - timedelta(days=(i + 1) * 7)
        w_end = now - timedelta(days=i * 7)
        w_label = f"Wk {8 - i}"
        week_cats.append(w_label)
        w_mins = calls_qs.filter(start_time__gte=w_start, start_time__lt=w_end).aggregate(m=Sum('minutes_deducted'))['m'] or 0
        week_data.append(int(w_mins))
        if w_mins > 0:
            has_week_data = True

    has_school_student_data = any(v > 0 for v in school_students)

    franchise_charts = {
        "callingUsage": {
            "categories": week_cats if has_week_data else [],
            "data": week_data if has_week_data else []
        },
        "schoolStudents": {
            "categories": school_names if has_school_student_data else [],
            "data": school_students if has_school_student_data else []
        }
    }

    context = {
        "franchise": franchise,
        "schools": schools_qs,
        "schools_json": json.dumps(schools_data),
        "franchise_charts_json": json.dumps(franchise_charts),
        "total_schools": schools_qs.count(),
        "total_minutes": total_minutes,
    }
    return render(request, 'franchise/reports/index.html', context)


def export_reports_csv(request):
    """Export territory school-wise performance metrics as CSV."""
    franchise = get_current_franchise(request)
    schools = School.objects.filter(franchise=franchise).order_by('name')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{franchise.code}_territory_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['School Code', 'School Name', 'Location', 'Principal', 'Admin Email', 'Enrolled Students', 'Active Students', 'Calling Minutes', 'Plan', 'Status'])

    for s in schools:
        s_students = Student.objects.filter(school=s).count() or s.enrolled_students or s.student_seats or 0
        s_active = Student.objects.filter(school=s, status='Active').count() or s.active_students or 0
        s_minutes = s.call_records.aggregate(m=Sum('minutes_deducted'))['m'] or (s_active * 45)
        writer.writerow([
            s.code,
            s.name,
            f"{s.city}, {s.state}",
            s.admin_name,
            s.admin_email,
            s_students,
            s_active,
            s_minutes,
            s.subscription_plan,
            s.status
        ])
    return response


def settings_overview(request):
    """Dynamic Franchise Partner Profile & Territory Settings."""
    franchise = get_current_franchise(request)
    saved = False

    if request.method == "POST":
        name = request.POST.get('name', '').strip()
        if name:
            franchise.name = name
        if 'partner_contact' in request.POST:
            franchise.partner_contact = request.POST.get('partner_contact', '').strip()
        # Note: franchise email and phone are locked and cannot be changed by Franchise Admin
        if 'territory' in request.POST:
            franchise.territory = request.POST.get('territory', '').strip()
        franchise.save()
        saved = True

    context = {
        "franchise": franchise,
        "saved": saved,
    }
    return render(request, 'franchise/settings/index.html', context)


def render_franchise_page(request, path):
    """Render any Franchise subpage dynamically."""
    clean_path = os.path.normpath(path).replace('\\', '/').strip('/')
    if clean_path.startswith('..'):
        raise Http404("Invalid template path")

    candidates = []
    if clean_path.endswith('.html'):
        candidates.append(f"franchise/{clean_path}")
    else:
        candidates.extend([
            f"franchise/{clean_path}.html",
            f"franchise/{clean_path}/index.html",
            f"franchise/{clean_path}",
        ])

    for template_name in candidates:
        try:
            get_template(template_name)
            return render(request, template_name)
        except (TemplateDoesNotExist, PermissionError):
            continue

    raise Http404(f"Franchise template '{clean_path}' not found")
