"""
Franchise Partner Views Implementation Source (franchise-views.py)
Source 2 Destination — Regional Operations Portal
Primary implementation source per AGENTS.md guidelines.
"""
import os
import json
from django.shortcuts import render, redirect
from django.http import Http404, HttpResponseBadRequest
from django.template.loader import get_template
from django.template import TemplateDoesNotExist
from django.db.models import Sum, Count, Q
from .models import (
    School, Franchise, Student, AcademicClass, ClassSection,
    GlobalDurationRule, CampusDurationRule, CallingScheduleRule,
    RechargePlan, StudentRecharge
)
from .calling_services import (
    get_global_duration_rule, ValidityService, RechargeService
)


def get_current_franchise(request):
    """Retrieve the active franchise partner (defaults to FRN-101 North-East EduNet Partners)."""
    code = request.GET.get('franchise_code') or request.session.get('franchise_code', 'FRN-101')
    franchise = Franchise.objects.filter(code=code).first()
    if not franchise:
        franchise = Franchise.objects.first()
    return franchise


def dashboard(request):
    """Render Franchise Partner Dashboard with live regional telemetry metrics."""
    franchise = get_current_franchise(request)
    schools_qs = School.objects.filter(franchise=franchise)
    total_campuses = schools_qs.count()
    active_campuses = schools_qs.filter(status='Active').count()
    students_qs = Student.objects.filter(school__franchise=franchise)
    db_students = students_qs.count()
    total_students = db_students if db_students > 0 else (schools_qs.aggregate(total=Sum('enrolled_students'))['total'] or 0)
    db_active = students_qs.filter(status='Active').count()
    active_students = db_active if db_active > 0 else (schools_qs.aggregate(total=Sum('active_students'))['total'] or 0)

    context = {
        "franchise": franchise,
        "total_campuses": total_campuses,
        "active_campuses": active_campuses,
        "total_students": total_students,
        "active_students": active_students,
    }
    return render(request, 'franchise/dashboard.html', context)


def schools_list(request):
    """Dynamic franchise assigned schools list view."""
    franchise = get_current_franchise(request)
    schools_qs = School.objects.filter(franchise=franchise).order_by('-id')
    total_campuses = schools_qs.count()
    active_campuses = schools_qs.filter(status='Active').count()
    total_students = schools_qs.aggregate(total=Sum('enrolled_students'))['total'] or 0

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
            "students": s.enrolled_students or s.student_seats,
            "studentSeats": s.student_seats,
            "activeStudents": s.active_students,
            "callingMinutes": s.active_students * 45,
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

        School.objects.create(
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
            emergency_calling_allowed=bool(request.POST.get('emergency_calling_allowed', True)),
            kiosk_group_tag=request.POST.get('kiosk_group_tag', 'AE-HOSTEL-BOOTH'),
            subscription_plan=request.POST.get('subscription_plan', 'Campus Growth Annual'),
            billing_cycle=request.POST.get('billing_cycle', 'Annually'),
            student_seats=seats,
            enrolled_students=seats,
            active_students=seats,
            status='Active',
            subscription_status="Active"
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
    students = school.students.all()[:20] if school else []

    context = {
        "school": school,
        "franchise": franchise,
        "students": students,
    }
    return render(request, 'franchise/schools/details.html', context)


def school_edit(request):
    """Franchise: Edit assigned school information."""
    school_id = request.GET.get('id')
    school = School.objects.filter(Q(code=school_id) | Q(id=school_id if str(school_id).isdigit() else 0)).first()
    if not school:
        school = School.objects.first()

    if request.method == "POST":
        school.name = request.POST.get('name', school.name)
        school.city = request.POST.get('city', school.city)
        school.admin_name = request.POST.get('admin_name', school.admin_name)
        school.admin_email = request.POST.get('admin_email', school.admin_email)
        school.admin_phone = request.POST.get('admin_phone', school.admin_phone)
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

    context = {
        "student": stu,
        "school": stu.school if stu else None,
        "franchise": stu.school.franchise if stu and stu.school else get_current_franchise(request),
    }
    return render(request, 'franchise/students/details.html', context)


def student_edit(request):
    """Franchise: Edit student calling profile and guardian contact numbers."""
    student_id = request.GET.get('id')
    stu = Student.objects.filter(Q(code=student_id) | Q(id=student_id if str(student_id).isdigit() else 0)).select_related('school').first()
    if not stu:
        stu = Student.objects.first()

    if request.method == "POST":
        stu.name = request.POST.get('name', stu.name)
        stu.class_name = request.POST.get('className', stu.class_name)
        stu.section = request.POST.get('section', stu.section)
        stu.primary_phone = request.POST.get('primaryPhone', stu.primary_phone)
        stu.secondary_phone = request.POST.get('secondaryPhone', stu.secondary_phone)
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

        Student.objects.create(
            code=code,
            calling_code=calling_code,
            name=name,
            gender=request.POST.get('gender', 'Male'),
            school=school,
            class_name=request.POST.get('className', 'Grade 10'),
            section=request.POST.get('section', 'Section A'),
            guardian_name=request.POST.get('guardianName', 'Authorized Guardian'),
            primary_phone=request.POST.get('primaryPhone', ''),
            remaining_minutes=120,
            daily_limit_min=school.daily_duration_cap if school else 15,
            wallet_balance=50.00,
            status='Active'
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
