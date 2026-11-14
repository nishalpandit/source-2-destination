"""
School Admin Views (school_views.py)
Source 2 Destination — Campus & Hostel Operations Portal
Handles campus-level student management, call allowances, and hostel phone operations.
"""
import os
import random
import json
from django.shortcuts import render, redirect
from django.http import Http404, HttpResponseBadRequest
from django.template.loader import get_template
from django.template import TemplateDoesNotExist
from django.db.models import Sum, Count, Q
from django.utils import timezone
from .models import (
    School, Franchise, Student, AcademicClass, ClassSection, Guardian, StudentStatusLog,
    GlobalDurationRule, CampusDurationRule, CallingScheduleRule, StudentScheduleException,
    RechargePlan, StudentRecharge
)
from .calling_services import (
    get_global_duration_rule, ValidityService, RechargeService,
    CallingDurationEngine, CallingScheduleEngine
)


def get_current_school(request):
    """Retrieve active school tenant (defaults to Oakridge Residential Academy SCH-1001)."""
    code = request.GET.get('school_code') or request.session.get('school_code', 'SCH-1001')
    school = School.objects.filter(code=code).first()
    if not school:
        school = School.objects.first()
    return school


def dashboard(request):
    """Render School Admin Primary Dashboard with live campus telemetry metrics."""
    school = get_current_school(request)
    students_qs = Student.objects.filter(school=school) if school else Student.objects.none()
    total_students = students_qs.count()
    active_students = students_qs.filter(status='Active').count()
    inactive_students = students_qs.filter(status__in=['Inactive', 'Suspended']).count()
    active_percent = round((active_students / total_students * 100), 1) if total_students > 0 else 0

    total_classes = AcademicClass.objects.filter(school=school).count()
    total_sections = ClassSection.objects.filter(school=school).count()
    total_guardians = Guardian.objects.filter(school=school).count()
    active_accounts = students_qs.filter(code_status='Active').count()
    total_minutes = students_qs.aggregate(total=Sum('remaining_minutes'))['total'] or 0

    # Expiring & grace accounts
    expiring_count = sum(1 for s in students_qs if s.validity_status in ['Expiring', 'Grace Period'])

    # Recent student additions and recharges
    recent_students = students_qs.order_by('-id')[:5]
    recent_recharges = StudentRecharge.objects.filter(school=school).select_related('student', 'plan').order_by('-created_at')[:5]
    recent_recharges_count = StudentRecharge.objects.filter(school=school).count()

    context = {
        "school": school,
        "total_students": total_students,
        "active_students": active_students,
        "inactive_students": inactive_students,
        "active_percent": active_percent,
        "total_classes": total_classes,
        "total_sections": total_sections,
        "total_guardians": total_guardians,
        "active_accounts": active_accounts,
        "total_minutes": total_minutes,
        "expiring_count": expiring_count,
        "recent_students": recent_students,
        "recent_recharges": recent_recharges,
        "recent_recharges_count": recent_recharges_count,
    }
    return render(request, 'school-admin/dashboard.html', context)


def students_list(request):
    """Dynamic campus student directory view."""
    school = get_current_school(request)
    students_qs = Student.objects.filter(school=school).order_by('-id') if school else Student.objects.none()
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
            "className": s.class_name,
            "section": s.section,
            "hostelWing": s.hostel_wing or "Boarding Wing",
            "guardianName": s.guardian_name,
            "guardianRelation": s.guardian_relation,
            "primaryPhone": s.primary_phone,
            "remainingMinutes": s.remaining_minutes,
            "dailyLimitMin": s.daily_limit_min,
            "validityExpiry": s.validity_expiry.strftime("%Y-%m-%d") if s.validity_expiry else "2027-05-31",
            "status": s.status
        }
        for s in students_qs
    ]

    context = {
        "school": school,
        "students": students_qs,
        "students_json": json.dumps(students_data),
        "total_students": total_students,
        "active_students": active_students,
    }
    return render(request, 'school-admin/students/list.html', context)


def student_add(request):
    """School Admin: Enroll new student on campus."""
    school = get_current_school(request)

    if request.method == "POST":
        name = request.POST.get('name', '').strip()
        if not name:
            return HttpResponseBadRequest("Student name is required.")

        code = request.POST.get('code') or f"STU-{Student.objects.count() + 4001}"
        calling_code = request.POST.get('studentCode') or f"S2D-{school.code[:3] if school else 'SCH'}-{Student.objects.count() + 8801}"

        Student.objects.create(
            code=code,
            calling_code=calling_code,
            name=name,
            gender=request.POST.get('gender', 'Male'),
            school=school,
            class_name=request.POST.get('className') or request.POST.get('class_name', 'Grade 10'),
            section=request.POST.get('section', 'Section A'),
            roll_number=request.POST.get('roll_number', ''),
            hostel_wing=request.POST.get('hostelWing') or request.POST.get('hostel_wing', ''),
            guardian_name=request.POST.get('guardianName') or request.POST.get('guardian_name', 'Authorized Guardian'),
            guardian_relation=request.POST.get('guardianRelation') or request.POST.get('guardian_relation', 'Father'),
            primary_phone=request.POST.get('primaryPhone') or request.POST.get('primary_phone', ''),
            secondary_phone=request.POST.get('secondaryPhone') or request.POST.get('secondary_phone', ''),
            remaining_minutes=int(request.POST.get('remainingMinutes') or 120),
            daily_limit_min=int(request.POST.get('dailyLimitMin') or (school.daily_duration_cap if school else 15)),
            wallet_balance=float(request.POST.get('wallet_balance') or 50.00),
            status=request.POST.get('status', 'Active')
        )
        return redirect('/school-admin/students/list.html')

    classes = AcademicClass.objects.filter(school=school).order_by('name') if school else AcademicClass.objects.none()
    sections = ClassSection.objects.filter(school=school).select_related('academic_class').order_by('name') if school else ClassSection.objects.none()

    context = {
        "school": school,
        "classes": classes,
        "sections": sections,
    }
    return render(request, 'school-admin/students/add.html', context)


def student_details(request):
    """School Admin: View 360 profile of student."""
    student_id = request.GET.get('id')
    stu = Student.objects.filter(Q(code=student_id) | Q(id=student_id if str(student_id).isdigit() else 0)).select_related('school').first()
    if not stu:
        stu = Student.objects.first()

    context = {
        "student": stu,
        "school": stu.school if stu else get_current_school(request),
    }
    return render(request, 'school-admin/students/details.html', context)


def student_edit(request):
    """School Admin: Edit student calling profile and guardian whitelist."""
    student_id = request.GET.get('id')
    stu = Student.objects.filter(Q(code=student_id) | Q(id=student_id if str(student_id).isdigit() else 0)).select_related('school').first()
    if not stu:
        stu = Student.objects.first()

    if request.method == "POST":
        stu.name = request.POST.get('name', stu.name)
        stu.class_name = request.POST.get('className', stu.class_name)
        stu.section = request.POST.get('section', stu.section)
        stu.hostel_wing = request.POST.get('hostelWing', stu.hostel_wing)
        stu.guardian_name = request.POST.get('guardianName', stu.guardian_name)
        stu.primary_phone = request.POST.get('primaryPhone', stu.primary_phone)
        if 'remainingMinutes' in request.POST:
            stu.remaining_minutes = int(request.POST['remainingMinutes'])
        if 'status' in request.POST:
            stu.status = request.POST['status']
        stu.save()
        return redirect(f"/school-admin/students/details.html?id={stu.code}")

    context = {
        "student": stu,
        "school": stu.school if stu else get_current_school(request),
    }
    return render(request, 'school-admin/students/edit.html', context)


def classes_list(request):
    """Dynamic School Admin Academic Classes Management."""
    school = get_current_school(request)

    if request.method == "POST":
        name = (request.POST.get('className') or request.POST.get('name') or '').strip()
        if name:
            supervisor = request.POST.get('supervisor', '').strip()
            daily_min = int(request.POST.get('defaultDailyMinutes') or request.POST.get('default_daily_minutes') or 15)
            digits = ''.join(c for c in name if c.isdigit())
            code = f"CLS-{digits}" if digits else f"CLS-{AcademicClass.objects.filter(school=school).count() + 1:02d}"

            AcademicClass.objects.get_or_create(
                school=school,
                name=name,
                defaults={
                    "code": code,
                    "supervisor": supervisor,
                    "default_daily_minutes": daily_min,
                    "schedule_group": request.POST.get('schedule_group', 'Standard Hostel Window'),
                    "status": "Active"
                }
            )
        return redirect('/school-admin/classes/list.html')

    classes_qs = AcademicClass.objects.filter(school=school, status='Active').order_by('name')
    classes_data = [
        {
            "id": c.code,
            "className": c.name,
            "supervisor": c.supervisor or "Faculty Coordinator",
            "sectionsCount": c.sections.filter(status='Active').count(),
            "studentsCount": Student.objects.filter(school=school, class_name__iexact=c.name).count(),
            "activeAccounts": Student.objects.filter(school=school, class_name__iexact=c.name, status='Active').count(),
            "defaultDailyMinutes": c.default_daily_minutes,
            "scheduleGroup": c.schedule_group,
            "status": c.status
        }
        for c in classes_qs
    ]

    context = {
        "school": school,
        "classes": classes_qs,
        "classes_json": json.dumps(classes_data),
        "total_classes": classes_qs.count(),
        "total_sections": ClassSection.objects.filter(school=school, status='Active').count(),
    }
    return render(request, 'school-admin/classes/list.html', context)


def sections_list(request):
    """Dynamic School Admin Sections Management."""
    school = get_current_school(request)

    if request.method == "POST":
        parent_class_name = request.POST.get('parent_class') or request.POST.get('className')
        parent_class = AcademicClass.objects.filter(
            Q(name__iexact=parent_class_name) | Q(code=parent_class_name),
            school=school
        ).first()
        section_name = (request.POST.get('sectionName') or request.POST.get('name') or '').strip()

        if parent_class and section_name:
            room_wing = (request.POST.get('roomWing') or request.POST.get('room_wing') or '').strip()
            advisor = (request.POST.get('advisor') or '').strip() or parent_class.supervisor
            booth = request.POST.get('assignedBooth') or 'North Hall Booth 1'

            cls_digits = ''.join(c for c in parent_class.name if c.isdigit())
            sec_letter = ''.join(c for c in section_name if c.isalpha())
            code = f"SEC-{cls_digits}{sec_letter[:1]}" if (cls_digits and sec_letter) else f"SEC-{ClassSection.objects.filter(school=school).count() + 1:02d}"

            ClassSection.objects.get_or_create(
                academic_class=parent_class,
                name=section_name,
                defaults={
                    "school": school,
                    "code": code,
                    "room_wing": room_wing,
                    "advisor": advisor,
                    "assigned_booth": booth,
                    "status": "Active"
                }
            )
        return redirect('/school-admin/classes/sections.html')

    classes_qs = AcademicClass.objects.filter(school=school, status='Active').order_by('name')
    sections_qs = ClassSection.objects.filter(school=school, status='Active').select_related('academic_class')

    sections_data = [
        {
            "id": s.code,
            "className": s.academic_class.name,
            "sectionName": s.name,
            "roomWing": s.room_wing or "Hostel Wing",
            "advisor": s.advisor or s.academic_class.supervisor or "Section Advisor",
            "studentsCount": Student.objects.filter(school=school, class_name__iexact=s.academic_class.name, section__iexact=s.name).count(),
            "activeCallers": Student.objects.filter(school=school, class_name__iexact=s.academic_class.name, section__iexact=s.name, status='Active').count(),
            "assignedBooth": s.assigned_booth,
            "status": s.status
        }
        for s in sections_qs
    ]

    context = {
        "school": school,
        "classes": classes_qs,
        "sections": sections_qs,
        "sections_json": json.dumps(sections_data),
        "total_sections": sections_qs.count(),
    }
    return render(request, 'school-admin/classes/sections.html', context)


def guardians_list(request):
    """Dynamic School Admin Parents & Guardians Directory."""
    school = get_current_school(request)
    guardians_qs = Guardian.objects.filter(school=school).select_related('student')
    total_guardians = guardians_qs.count()
    active_guardians = guardians_qs.filter(status='Active').count()

    guardians_data = [
        {
            "id": g.code,
            "code": g.code,
            "name": g.name,
            "studentName": g.student.name if g.student else "Unassigned",
            "className": f"{g.student.class_name} · {g.student.section}" if g.student else "",
            "relation": g.relation,
            "email": g.email,
            "fatherPhone": g.father_phone or "N/A",
            "motherPhone": g.mother_phone or "N/A",
            "verification": g.verification,
            "whitelistStatus": g.whitelist_status,
            "status": g.status
        }
        for g in guardians_qs
    ]

    context = {
        "school": school,
        "guardians": guardians_qs,
        "guardians_json": json.dumps(guardians_data),
        "total_guardians": total_guardians,
        "active_guardians": active_guardians,
    }
    return render(request, 'school-admin/guardians/list.html', context)


def guardian_add(request):
    """School Admin: Register & whitelist authorized parent/guardian numbers."""
    school = get_current_school(request)

    if request.method == "POST":
        student_id = request.POST.get('student_id')
        student = Student.objects.filter(Q(code=student_id) | Q(id=student_id if str(student_id).isdigit() else 0)).first()
        if not student:
            student = Student.objects.filter(school=school).first()

        name = (request.POST.get('name') or '').strip()
        relation = request.POST.get('relation', 'Father')
        father_phone = (request.POST.get('fatherPhone') or request.POST.get('father_phone') or '').strip()
        mother_phone = (request.POST.get('motherPhone') or request.POST.get('mother_phone') or '').strip()
        emergency_phone = (request.POST.get('emergencyPhone') or request.POST.get('emergency_phone') or '').strip()
        email = (request.POST.get('email') or '').strip()
        verification = request.POST.get('verification', 'KYC Verified (School Admission File)')

        code = f"GRD-{Guardian.objects.count() + 501}"
        active_numbers = [p for p in [father_phone, mother_phone, emergency_phone] if p and p != 'N/A']
        whitelist_label = f"Authorized ({len(active_numbers)} Number{'s' if len(active_numbers) != 1 else ''})"

        Guardian.objects.create(
            school=student.school if student else school,
            student=student,
            code=code,
            name=name,
            relation=relation,
            father_phone=father_phone,
            mother_phone=mother_phone,
            emergency_phone=emergency_phone,
            email=email,
            verification=verification,
            whitelist_status=whitelist_label,
            status='Active'
        )
        return redirect('/school-admin/guardians/list.html')

    students = Student.objects.filter(school=school).order_by('name')
    context = {
        "school": school,
        "students": students,
    }
    return render(request, 'school-admin/guardians/add.html', context)


def guardian_details(request):
    """School Admin: View guardian whitelist profile & verified contact details."""
    guardian_id = request.GET.get('id')
    guardian = Guardian.objects.filter(Q(code=guardian_id) | Q(id=guardian_id if str(guardian_id).isdigit() else 0)).select_related('student', 'school').first()
    if not guardian:
        guardian = Guardian.objects.first()

    context = {
        "guardian": guardian,
        "student": guardian.student if guardian else None,
        "school": guardian.school if guardian else get_current_school(request),
    }
    return render(request, 'school-admin/guardians/details.html', context)


def guardian_edit(request):
    """School Admin: Modify authorized phone numbers or pause dialer authorization."""
    guardian_id = request.GET.get('id')
    guardian = Guardian.objects.filter(Q(code=guardian_id) | Q(id=guardian_id if str(guardian_id).isdigit() else 0)).select_related('student', 'school').first()
    if not guardian:
        guardian = Guardian.objects.first()

    if request.method == "POST":
        guardian.name = request.POST.get('name', guardian.name)
        guardian.email = request.POST.get('email', guardian.email)
        guardian.father_phone = request.POST.get('fatherPhone', guardian.father_phone)
        guardian.mother_phone = request.POST.get('motherPhone', guardian.mother_phone)
        if 'status' in request.POST:
            guardian.status = request.POST.get('status')

        active_numbers = [p for p in [guardian.father_phone, guardian.mother_phone, guardian.emergency_phone] if p and p != 'N/A']
        guardian.whitelist_status = f"Authorized ({len(active_numbers)} Number{'s' if len(active_numbers) != 1 else ''})"
        guardian.save()
        return redirect(f"/school-admin/guardians/details.html?id={guardian.code}")

    context = {
        "guardian": guardian,
        "student": guardian.student if guardian else None,
        "school": guardian.school if guardian else get_current_school(request),
    }
    return render(request, 'school-admin/guardians/edit.html', context)


def student_codes(request):
    """
    School Admin: Unique Student Calling Codes Management.
    Atomically generates, rotates, and assigns collision-free kiosk login codes.
    """
    school = get_current_school(request)
    students = Student.objects.filter(school=school).order_by('name')

    issued_info = None

    if request.method == "POST":
        student_id = request.POST.get('student_id')
        pin_policy = request.POST.get('pin_policy', 'Unique Code + 4-Digit Student PIN')
        action = request.POST.get('action', 'issue')

        student = Student.objects.filter(
            Q(code=student_id) | Q(calling_code=student_id) | Q(id=student_id if str(student_id).isdigit() else 0),
            school=school
        ).first()

        if student:
            if action in ['suspend', 'suspend_code']:
                student.code_status = 'Suspended'
                student.save(update_fields=['code_status'])
            elif action in ['activate', 'activate_code']:
                student.code_status = 'Active'
                student.save(update_fields=['code_status'])
            else:
                # Generate collision-free calling code (e.g. S2D-OAK-XXXX)
                campus_tag = "OAK"
                if school and school.name:
                    words = [w for w in school.name.split() if w.upper() not in ['ACADEMY', 'SCHOOL', 'COLLEGIATE', 'CAMPUS', 'HOSTEL', 'RESIDENTIAL']]
                    if words:
                        campus_tag = words[0][:3].upper()

                while True:
                    candidate_code = f"S2D-{campus_tag}-{random.randint(1000, 9999)}"
                    if not Student.objects.filter(calling_code=candidate_code).exists():
                        break

                student.calling_code = candidate_code
                student.pin_policy = pin_policy
                student.code_status = 'Active'
                student.code_issued_at = timezone.now()
                student.save()
                issued_info = {
                    "student_name": student.name,
                    "code": candidate_code,
                    "pin_policy": pin_policy
                }

    # Prepare client-side payload matching table specs
    student_codes_data = [
        {
            "id": f"COD-{s.id}",
            "code": s.calling_code,
            "studentId": s.code,
            "studentName": s.name,
            "className": f"{s.class_name} · {s.section}",
            "issuedBy": "Backend Auth Engine",
            "issuedAt": s.code_issued_at.strftime("%Y-%m-%d %H:%M") if s.code_issued_at else "2026-08-01 10:00",
            "lastUsed": s.code_last_used.strftime("%Y-%m-%d %H:%M") if s.code_last_used else "Never",
            "pinPolicy": s.pin_policy,
            "status": s.code_status
        }
        for s in students
    ]

    context = {
        "school": school,
        "students": students,
        "student_codes_json": json.dumps(student_codes_data),
        "issued_info": issued_info,
        "total_codes": students.count(),
        "active_codes": students.filter(code_status='Active').count(),
        "suspended_codes": students.filter(code_status='Suspended').count(),
    }
    return render(request, 'school-admin/student-codes/index.html', context)


def student_status(request):
    """
    School Admin: Student Account Lifecycle & Activation / Deactivation.
    Handles activation, temporary suspension, disciplinary holds, and audit logging.
    """
    school = get_current_school(request)
    students = Student.objects.filter(school=school).order_by('name')

    status_message = None

    if request.method == "POST":
        student_id = request.POST.get('student_id')
        new_status = request.POST.get('status', 'Active')
        reason = (request.POST.get('reason') or 'Administrative review').strip()
        authorized_by = (request.POST.get('authorized_by') or 'School Administrator').strip()

        student = Student.objects.filter(
            Q(code=student_id) | Q(calling_code=student_id) | Q(id=student_id if str(student_id).isdigit() else 0),
            school=school
        ).first()

        if student and new_status in ['Active', 'Inactive', 'Suspended']:
            prev_status = student.status
            student.status = new_status
            if new_status == 'Suspended':
                student.code_status = 'Suspended'
            elif new_status == 'Active':
                student.code_status = 'Active'
            student.save()

            StudentStatusLog.objects.create(
                student=student,
                school=school,
                previous_status=prev_status,
                new_status=new_status,
                reason=reason,
                authorized_by=authorized_by
            )
            status_message = f"Status for {student.name} transitioned from {prev_status} to {new_status}."

    status_logs = StudentStatusLog.objects.filter(school=school).select_related('student').order_by('-timestamp')[:50]

    # Prepare students data for table
    students_data = [
        {
            "id": s.code,
            "code": s.code,
            "studentCode": s.calling_code,
            "name": s.name,
            "gender": s.gender,
            "schoolId": s.school.code,
            "school": s.school.name,
            "className": s.class_name,
            "section": s.section,
            "hostelWing": s.hostel_wing or "Boarding Wing",
            "guardianName": s.guardian_name,
            "guardianRelation": s.guardian_relation,
            "primaryPhone": s.primary_phone,
            "remainingMinutes": s.remaining_minutes,
            "dailyLimitMin": s.daily_limit_min,
            "validityExpiry": s.validity_expiry.strftime("%Y-%m-%d") if s.validity_expiry else "2027-05-31",
            "status": s.status
        }
        for s in students
    ]

    context = {
        "school": school,
        "students": students,
        "status_logs": status_logs,
        "students_json": json.dumps(students_data),
        "status_message": status_message,
        "total_students": students.count(),
        "active_count": students.filter(status='Active').count(),
        "inactive_count": students.filter(status='Inactive').count(),
        "suspended_count": students.filter(status='Suspended').count(),
    }
    return render(request, 'school-admin/student-status/index.html', context)


def calling_duration(request):
    """School Admin: Configure campus, wing, and class calling duration limits."""
    school = get_current_school(request)
    global_rule = get_global_duration_rule()

    if request.method == "POST":
        scope = request.POST.get('scope', 'School-Wide Default')
        max_call = min(global_rule.hard_max_call_duration, int(request.POST.get('max_call', 15)))
        daily_limit = min(global_rule.max_daily_student_cap, int(request.POST.get('daily_limit', 15)))

        rule, _ = CampusDurationRule.objects.get_or_create(school=school, scope=scope)
        rule.max_call_duration = max_call
        rule.daily_cumulative_limit = daily_limit
        rule.save()

        if scope == 'School-Wide Default':
            school.daily_duration_cap = daily_limit
            school.save(update_fields=['daily_duration_cap'])

        return redirect('/school-admin/calling-duration/index.html')

    standard_rule = CampusDurationRule.objects.filter(school=school, scope="School-Wide Default").first()
    junior_rule = CampusDurationRule.objects.filter(school=school, scope="Grades 7–8 (Junior Wing)").first()

    context = {
        "school": school,
        "global_rule": global_rule,
        "standard_cap": standard_rule.max_call_duration if standard_rule else school.daily_duration_cap or 15,
        "junior_cap": junior_rule.max_call_duration if junior_rule else 10,
    }
    return render(request, 'school-admin/calling-duration/index.html', context)


def calling_schedules(request):
    """School Admin: School, class, and student-wise calling schedules and exception windows."""
    school = get_current_school(request)

    if request.method == "POST":
        student_id = request.POST.get('student_id')
        allowed_window = request.POST.get('allowed_window', '06:30 – 07:15').strip()
        valid_until = request.POST.get('valid_until')

        student = Student.objects.filter(
            Q(code=student_id) | Q(calling_code=student_id) | Q(id=student_id if str(student_id).isdigit() else 0),
            school=school
        ).first()

        if student and allowed_window and valid_until:
            StudentScheduleException.objects.create(
                student=student,
                allowed_window=allowed_window,
                valid_until=valid_until,
                reason="International timezone guardian calling exemption"
            )
        return redirect('/school-admin/calling-schedules/index.html')

    students = Student.objects.filter(school=school).order_by('name')
    classes = AcademicClass.objects.filter(school=school).order_by('name')
    exceptions = StudentScheduleException.objects.filter(student__school=school).select_related('student')

    classes_data = [
        {
            "id": c.code,
            "className": c.name,
            "supervisor": c.supervisor,
            "sectionsCount": c.sections.filter(status='Active').count(),
            "studentsCount": Student.objects.filter(school=school, class_name__iexact=c.name).count(),
            "defaultDailyMinutes": c.default_daily_minutes,
            "scheduleGroup": c.schedule_group,
            "status": c.status
        }
        for c in classes
    ]

    context = {
        "school": school,
        "students": students,
        "classes": classes,
        "classes_json": json.dumps(classes_data),
        "exceptions": exceptions,
    }
    return render(request, 'school-admin/calling-schedules/index.html', context)


def validity_overview(request):
    """School Admin: Student account validity & expiring accounts monitoring."""
    school = get_current_school(request)
    students_qs = Student.objects.filter(school=school).order_by('-id')

    students_data = [
        {
            "id": s.code,
            "name": s.name,
            "studentCode": s.calling_code,
            "school": school.name,
            "validityStart": s.validity_start.strftime("%Y-%m-%d") if s.validity_start else "-",
            "validityExpiry": s.validity_expiry.strftime("%Y-%m-%d") if s.validity_expiry else "-",
            "remainingMinutes": s.remaining_minutes,
            "validityStatus": ValidityService.evaluate(s)["status"],
            "status": s.status,
        }
        for s in students_qs
    ]

    context = {
        "school": school,
        "students": students_qs,
        "students_json": json.dumps(students_data),
    }
    return render(request, 'school-admin/validity/index.html', context)


def recharges_overview(request):
    """School Admin: Recharge desk overview and history."""
    school = get_current_school(request)
    recharges_qs = StudentRecharge.objects.filter(school=school).select_related('student', 'plan').order_by('-created_at')

    recharges_data = [
        {
            "id": r.recharge_id,
            "date": r.created_at.strftime("%Y-%m-%d %H:%M"),
            "studentName": r.student.name,
            "studentCode": r.student.calling_code,
            "school": school.name,
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
        "recharges": recharges_qs,
        "recharges_json": json.dumps(recharges_data),
    }
    return render(request, 'school-admin/recharges/overview.html', context)


def student_recharge(request):
    """School Admin: Initiate student account recharge and top-up calling minutes."""
    school = get_current_school(request)
    students = Student.objects.filter(school=school).order_by('name')
    plans = RechargePlan.objects.filter(status='Active').order_by('price')

    if request.method == "POST":
        student_id = request.POST.get('student_id')
        plan_id = request.POST.get('plan_id')
        payment_mode = request.POST.get('payment_mode', 'Campus Bursar Desk Ledger')
        voucher_ref = request.POST.get('voucher_ref', '')

        student = Student.objects.filter(
            Q(code=student_id) | Q(calling_code=student_id) | Q(id=student_id if str(student_id).isdigit() else 0),
            school=school
        ).first()
        plan = RechargePlan.objects.filter(
            Q(code=plan_id) | Q(id=plan_id if str(plan_id).isdigit() else 0)
        ).first()

        if student and plan:
            RechargeService.process_recharge(
                student=student,
                plan=plan,
                payment_mode=payment_mode,
                voucher_ref=voucher_ref
            )
        return redirect('/school-admin/recharges/overview.html')

    context = {
        "school": school,
        "students": students,
        "plans": plans,
    }
    return render(request, 'school-admin/recharges/student-recharge.html', context)


def render_school_page(request, path):
    """Render any School Admin subpage dynamically."""
    clean_path = os.path.normpath(path).replace('\\', '/').strip('/')
    if clean_path.startswith('..'):
        raise Http404("Invalid template path")

    candidates = []
    if clean_path.endswith('.html'):
        candidates.append(f"school-admin/{clean_path}")
    else:
        candidates.extend([
            f"school-admin/{clean_path}.html",
            f"school-admin/{clean_path}/index.html",
            f"school-admin/{clean_path}",
        ])

    for template_name in candidates:
        try:
            get_template(template_name)
            return render(request, template_name)
        except (TemplateDoesNotExist, PermissionError):
            continue

    raise Http404(f"School Admin template '{clean_path}' not found")
