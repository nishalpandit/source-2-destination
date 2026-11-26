import os
import io
import csv
import random
import json
from datetime import date, timedelta
from django.shortcuts import render, redirect
from django.http import Http404, HttpResponse, HttpResponseBadRequest, JsonResponse
from django.template.loader import get_template
from django.template import TemplateDoesNotExist
from django.db.models import Sum, Count, Q
from django.db import transaction
from django.utils import timezone
from .models import (
    School, Franchise, Student, AcademicClass, ClassSection, Guardian, StudentStatusLog,
    GlobalDurationRule, CampusDurationRule, CallingScheduleRule, StudentScheduleException,
    RechargePlan, StudentRecharge, ValidityExtensionLog,
    CallRecord, KioskDevice, DeviceAssignment, HostelWarden
)
from .calling_services import (
    get_global_duration_rule, ValidityService, RechargeService,
    CallingDurationEngine, CallingScheduleEngine
)


def get_current_school(request):
    """
    Resolve active school tenant:
    1. Explicit query parameter (?school_code=...) saved into session when valid
    2. Persisted session school_code
    3. Authenticated user's matched school by admin_email
    4. Default campus fallback (SCH-1001 or first available School)
    """
    query_code = (request.GET.get('school_code') or '').strip()
    if query_code:
        school = School.objects.filter(code=query_code).first()
        if school:
            request.session['school_code'] = school.code
            return school

    session_code = request.session.get('school_code')
    if session_code:
        school = School.objects.filter(code=session_code).first()
        if school:
            return school

    if getattr(request, 'user', None) and request.user.is_authenticated and request.user.email:
        school = School.objects.filter(admin_email__iexact=request.user.email).first()
        if school:
            return school

    return School.objects.filter(code='SCH-1001').first() or School.objects.first()


# --- 1. PRIMARY CAMPUS DASHBOARD ---
def dashboard(request):
    """Render School Admin Primary Dashboard with live campus telemetry metrics."""
    school = get_current_school(request)
    students_qs = Student.objects.filter(school=school) if school else Student.objects.none()
    total_students = students_qs.count()
    active_students = students_qs.filter(status='Active').count()
    inactive_students = students_qs.filter(status__in=['Inactive', 'Suspended']).count()
    active_percent = round((active_students / total_students * 100), 1) if total_students > 0 else 0

    total_classes = AcademicClass.objects.filter(school=school).count() if school else 0
    total_sections = ClassSection.objects.filter(school=school).count() if school else 0
    total_guardians = Guardian.objects.filter(school=school).count() if school else 0
    active_accounts = students_qs.filter(code_status='Active').count()
    total_minutes = students_qs.aggregate(total=Sum('remaining_minutes'))['total'] or 0

    # Expiring & grace accounts
    expiring_count = sum(1 for s in students_qs if s.validity_status in ['Expiring', 'Grace Period'])

    # Recent student additions and recharges
    recent_students = students_qs.order_by('-id')[:5]
    recent_recharges = StudentRecharge.objects.filter(school=school).select_related('student', 'plan').order_by('-created_at')[:5] if school else []
    recent_recharges_count = StudentRecharge.objects.filter(school=school).count() if school else 0

    # Accurate Today-Only Calling Telemetry & Whitelist Compliance
    today = timezone.localdate()
    calls_today_qs = CallRecord.objects.filter(school=school, start_time__date=today) if school else CallRecord.objects.none()
    calls_today_count = calls_today_qs.count()
    calls_completed_today = calls_today_qs.filter(call_status='Completed').count()
    violations_today_count = calls_today_qs.filter(
        call_status__in=['Restricted Schedule', 'Unauthorized Number']
    ).count()
    unauthorized_today_count = calls_today_qs.filter(call_status='Unauthorized Number').count()
    whitelist_compliance_percent = (
        round(((calls_today_count - unauthorized_today_count) / calls_today_count) * 100, 1)
        if calls_today_count > 0 else 100.0
    )

    # Kiosk Booth Fleet Health
    total_booths_count = KioskDevice.objects.filter(school=school).count() if school else 0
    booths_online_count = KioskDevice.objects.filter(school=school, status='Online').count() if school else 0
    booths_online_percent = (
        round((booths_online_count / total_booths_count) * 100, 1)
        if total_booths_count > 0 else 0.0
    )

    # Hostel Wardens On-Duty Roster
    wardens_on_duty_count = HostelWarden.objects.filter(school=school, status='On Duty').count() if school else 0
    recent_wardens = HostelWarden.objects.filter(school=school).order_by('status', 'name')[:4] if school else []

    # Live Chart 1: Multi-Range Calling Traffic (30 Days, 6 Months, 12 Months)
    year_ago = today - timedelta(days=366)
    calls_year = list(
        CallRecord.objects.filter(school=school, start_time__date__gte=year_ago)
        .values('start_time', 'call_status')
    ) if school else []

    restricted_statuses = {'Restricted Schedule', 'Unauthorized Number', 'Insufficient Credits'}

    # 1. 30 Days (Daily)
    day_map_completed = {}
    day_map_restricted = {}
    for r in calls_year:
        st = r['start_time']
        d = st.date() if hasattr(st, 'date') else st
        if r['call_status'] == 'Completed':
            day_map_completed[d] = day_map_completed.get(d, 0) + 1
        elif r['call_status'] in restricted_statuses:
            day_map_restricted[d] = day_map_restricted.get(d, 0) + 1

    labels_30d = []
    completed_30d = []
    restricted_30d = []
    for offset in range(29, -1, -1):
        day = today - timedelta(days=offset)
        labels_30d.append('Today' if offset == 0 else day.strftime('%b %d'))
        completed_30d.append(day_map_completed.get(day, 0))
        restricted_30d.append(day_map_restricted.get(day, 0))

    # 2. 6 Months (Monthly)
    labels_6m = []
    completed_6m = []
    restricted_6m = []
    for m_offset in range(5, -1, -1):
        tot = today.year * 12 + today.month - 1 - m_offset
        yr = tot // 12
        mo = (tot % 12) + 1
        labels_6m.append(date(yr, mo, 1).strftime('%b'))
        c_count = 0
        r_count = 0
        for r in calls_year:
            st = r['start_time']
            if st.year == yr and st.month == mo:
                if r['call_status'] == 'Completed':
                    c_count += 1
                elif r['call_status'] in restricted_statuses:
                    r_count += 1
        completed_6m.append(c_count)
        restricted_6m.append(r_count)

    # 3. 12 Months (Monthly)
    labels_12m = []
    completed_12m = []
    restricted_12m = []
    for m_offset in range(11, -1, -1):
        tot = today.year * 12 + today.month - 1 - m_offset
        yr = tot // 12
        mo = (tot % 12) + 1
        labels_12m.append(date(yr, mo, 1).strftime('%b'))
        c_count = 0
        r_count = 0
        for r in calls_year:
            st = r['start_time']
            if st.year == yr and st.month == mo:
                if r['call_status'] == 'Completed':
                    c_count += 1
                elif r['call_status'] in restricted_statuses:
                    r_count += 1
        completed_12m.append(c_count)
        restricted_12m.append(r_count)

    daily_calls_chart = {
        "ranges": {
            "30D": {
                "labels": labels_30d,
                "completed": completed_30d,
                "restricted": restricted_30d,
            },
            "6M": {
                "labels": labels_6m,
                "completed": completed_6m,
                "restricted": restricted_6m,
            },
            "12M": {
                "labels": labels_12m,
                "completed": completed_12m,
                "restricted": restricted_12m,
            }
        },
        "labels": labels_30d,
        "completed": completed_30d,
        "restricted": restricted_30d,
        "hasData": bool(calls_year),
    }

    # Live Chart 2: 30-Day Class-wise Voice Usage Breakdown
    thirty_days_ago = today - timedelta(days=30)
    academic_classes = list(AcademicClass.objects.filter(school=school).order_by('name')) if school else []
    class_names = [c.name for c in academic_classes]
    if not class_names and school:
        class_names = list(
            students_qs.exclude(class_name='').values_list('class_name', flat=True).distinct().order_by('class_name')
        )

    class_usage_labels = []
    class_usage_minutes = []
    for cname in class_names:
        mins = CallRecord.objects.filter(
            school=school,
            student__class_name__iexact=cname,
            start_time__date__gte=thirty_days_ago
        ).aggregate(total=Sum('minutes_deducted'))['total'] or 0
        class_usage_labels.append(cname)
        class_usage_minutes.append(int(mins))

    class_usage_chart = {
        "labels": class_usage_labels,
        "minutes": class_usage_minutes,
        "hasData": bool(class_usage_labels),
    }

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
        "calls_today_count": calls_today_count,
        "calls_completed_today": calls_completed_today,
        "violations_today_count": violations_today_count,
        "whitelist_compliance_percent": whitelist_compliance_percent,
        "total_booths_count": total_booths_count,
        "booths_online_count": booths_online_count,
        "booths_online_percent": booths_online_percent,
        "wardens_on_duty_count": wardens_on_duty_count,
        "recent_wardens": recent_wardens,
        "daily_calls_chart_json": json.dumps(daily_calls_chart),
        "class_usage_chart_json": json.dumps(class_usage_chart),
    }
    return render(request, 'school-admin/dashboard.html', context)


# --- 2. STUDENT MANAGEMENT (DIRECTORY, ENROLL, 360 DETAILS, EDIT) ---
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
        name = (request.POST.get('name') or request.POST.get('student_name') or '').strip()
        if not name:
            return HttpResponseBadRequest("Student name is required.")

        code = request.POST.get('code') or f"STU-{Student.objects.count() + 4001}"
        calling_code = request.POST.get('studentCode') or f"S2D-{school.code[:3] if school else 'SCH'}-{Student.objects.count() + 8801}"

        validity_expiry = request.POST.get('validity_expiry') or request.POST.get('validityExpiry')
        if not validity_expiry:
            validity_expiry = timezone.now().date() + timedelta(days=365)

        dob = request.POST.get('date_of_birth') or request.POST.get('dob')
        pin = (request.POST.get('pin') or '1234').strip()

        stu = Student.objects.create(
            code=code,
            calling_code=calling_code,
            name=name,
            gender=request.POST.get('gender', 'Male'),
            date_of_birth=dob if dob else None,
            school=school,
            class_name=request.POST.get('className') or request.POST.get('class_name', 'Grade 10'),
            section=request.POST.get('section', 'Section A'),
            roll_number=request.POST.get('roll_number') or request.POST.get('rollNumber', ''),
            hostel_wing=request.POST.get('hostelWing') or request.POST.get('hostel_wing', 'North Wing'),
            guardian_name=request.POST.get('guardianName') or request.POST.get('guardian_name', 'Authorized Guardian'),
            guardian_relation=request.POST.get('guardianRelation') or request.POST.get('guardian_relation', 'Father'),
            primary_phone=request.POST.get('primaryPhone') or request.POST.get('primary_phone', ''),
            secondary_phone=request.POST.get('secondaryPhone') or request.POST.get('secondary_phone', ''),
            remaining_minutes=int(request.POST.get('remainingMinutes') or 120),
            daily_limit_min=int(request.POST.get('dailyLimitMin') or (school.daily_duration_cap if school else 15)),
            wallet_balance=float(request.POST.get('wallet_balance') or 50.00),
            validity_expiry=validity_expiry,
            pin=pin,
            status=request.POST.get('status', 'Active')
        )

        # Create linked KYC Guardian record
        Guardian.objects.create(
            school=school,
            student=stu,
            code=f"GRD-{Guardian.objects.count() + 501}",
            name=stu.guardian_name,
            relation=stu.guardian_relation,
            father_phone=stu.primary_phone,
            mother_phone=stu.secondary_phone,
            whitelist_status="Authorized (1 Number)" if stu.primary_phone else "Pending",
            verification="KYC Verified (School Admission File)",
            status='Active'
        )

        # Link selected booth if specified
        device_id = request.POST.get('device_id')
        if device_id and school:
            device = KioskDevice.objects.filter(device_id=device_id, school=school).first()
            if device:
                DeviceAssignment.objects.create(
                    school=school,
                    device=device,
                    hostel_wing=stu.hostel_wing or device.hostel_block,
                    academic_class=stu.class_name,
                    assigned_by=request.user.get_full_name() if getattr(request, 'user', None) and request.user.is_authenticated and request.user.get_full_name() else "School Admin",
                    status='Active'
                )

        return redirect('/school-admin/students/list.html')

    classes = AcademicClass.objects.filter(school=school).order_by('name') if school else AcademicClass.objects.none()
    sections = ClassSection.objects.filter(school=school).select_related('academic_class').order_by('name') if school else ClassSection.objects.none()
    devices = KioskDevice.objects.filter(school=school).order_by('name') if school else KioskDevice.objects.none()

    context = {
        "school": school,
        "classes": classes,
        "sections": sections,
        "devices": devices,
    }
    return render(request, 'school-admin/students/add.html', context)


def student_details(request):
    """School Admin: View 360 profile of student."""
    school = get_current_school(request)
    student_id = request.GET.get('id')
    stu = Student.objects.filter(
        Q(code=student_id) | Q(id=student_id if str(student_id).isdigit() else 0)
    ).select_related('school').first()
    if not stu:
        stu = Student.objects.filter(school=school).select_related('school').first() or Student.objects.select_related('school').first()

    guardians = Guardian.objects.filter(student=stu) if stu else []
    calls = CallRecord.objects.filter(student=stu).select_related('guardian', 'school').order_by('-start_time')[:20] if stu else []
    recharges = StudentRecharge.objects.filter(student=stu).select_related('plan', 'school').order_by('-created_at')[:20] if stu else []

    call_history_data = [
        {
            "id": c.call_id,
            "studentName": stu.name if stu else "Student",
            "studentCode": stu.calling_code if stu else "N/A",
            "school": c.school.name if c.school else "",
            "authorizedNumber": c.destination_number,
            "guardianName": c.guardian.name if c.guardian else c.call_type,
            "startTime": c.start_time.strftime("%Y-%m-%d %H:%M"),
            "duration": f"{c.duration_seconds // 60}m {c.duration_seconds % 60:02d}s" if c.duration_seconds > 0 else "0m 00s",
            "minutesUsed": c.minutes_deducted,
            "status": c.call_status,
            "dateOnly": c.start_time.strftime("%Y-%m-%d"),
            "recordingUrl": c.audio_recording_url,
        }
        for c in calls
    ]

    recharges_data = [
        {
            "id": r.recharge_id,
            "date": r.created_at.strftime("%Y-%m-%d %H:%M"),
            "studentName": stu.name if stu else "Student",
            "studentCode": stu.calling_code if stu else "N/A",
            "school": r.school.name if r.school else "",
            "planName": r.plan_name_cache,
            "minutesAdded": r.minutes_added,
            "validityDays": r.validity_days_added,
            "amount": float(r.amount),
            "status": r.status,
            "paymentMode": r.payment_mode,
            "voucherRef": r.voucher_ref,
        }
        for r in recharges
    ]

    context = {
        "student": stu,
        "guardians": guardians,
        "calls": calls,
        "recharges": recharges,
        "call_history_json": json.dumps(call_history_data),
        "recharges_json": json.dumps(recharges_data),
        "school": stu.school if stu else school,
    }
    return render(request, 'school-admin/students/details.html', context)


def student_edit(request):
    """School Admin: Edit student calling profile and guardian whitelist."""
    student_id = request.GET.get('id')
    stu = Student.objects.filter(Q(code=student_id) | Q(id=student_id if str(student_id).isdigit() else 0)).select_related('school').first()
    if not stu:
        stu = Student.objects.first()

    if request.method == "POST" and stu:
        stu.name = request.POST.get('name', stu.name).strip()
        stu.gender = request.POST.get('gender', stu.gender)
        dob = request.POST.get('date_of_birth') or request.POST.get('dob')
        if dob:
            stu.date_of_birth = dob
        if request.POST.get('pin'):
            stu.pin = request.POST['pin'].strip()
        if request.POST.get('wallet_balance'):
            try:
                stu.wallet_balance = float(request.POST['wallet_balance'])
            except ValueError:
                pass
        stu.class_name = (request.POST.get('className') or request.POST.get('class_name', stu.class_name)).strip()
        stu.section = (request.POST.get('section', stu.section)).strip()
        stu.roll_number = (request.POST.get('roll_number') or request.POST.get('rollNumber', stu.roll_number)).strip()
        stu.hostel_wing = (request.POST.get('hostelWing') or request.POST.get('hostel_wing', stu.hostel_wing)).strip()
        stu.guardian_name = (request.POST.get('guardianName') or request.POST.get('guardian_name', stu.guardian_name)).strip()
        stu.primary_phone = (request.POST.get('primaryPhone') or request.POST.get('primary_phone', stu.primary_phone)).strip()
        if request.POST.get('secondaryPhone') or request.POST.get('secondary_phone'):
            stu.secondary_phone = (request.POST.get('secondaryPhone') or request.POST.get('secondary_phone')).strip()

        expiry_val = request.POST.get('validityExpiry') or request.POST.get('validity_expiry')
        if expiry_val:
            stu.validity_expiry = expiry_val

        if 'remainingMinutes' in request.POST:
            stu.remaining_minutes = int(request.POST['remainingMinutes'])
        if 'dailyLimitMin' in request.POST:
            stu.daily_limit_min = int(request.POST['dailyLimitMin'])
        if 'status' in request.POST:
            stu.status = request.POST['status']
        stu.save()

        # Keep linked Guardian contact numbers and name in sync
        guardian = stu.guardian_contacts.first()
        if guardian:
            guardian.name = stu.guardian_name
            guardian.father_phone = stu.primary_phone
            if stu.secondary_phone:
                guardian.mother_phone = stu.secondary_phone
            active_nums = [p for p in [guardian.father_phone, guardian.mother_phone, guardian.emergency_phone] if p and p != 'N/A']
            guardian.whitelist_status = f"Authorized ({len(active_nums)} Number{'s' if len(active_nums) != 1 else ''})"
            guardian.save()

        return redirect(f"/school-admin/students/details.html?id={stu.code}")

    context = {
        "student": stu,
        "school": stu.school if stu else get_current_school(request),
    }
    return render(request, 'school-admin/students/edit.html', context)


# --- 3. BULK STUDENT EXCEL / CSV UPLOAD ---
def download_sample_csv(request):
    """Stream formatted CSV template for bulk student enrollment."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="student_bulk_upload_sample.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'student_full_name', 'gender', 'class_grade', 'section',
        'hostel_wing', 'guardian_name', 'relation',
        'father_authorized_phone', 'mother_authorized_phone',
        'allocated_minutes', 'daily_limit_minutes'
    ])
    writer.writerow(['Aarav Sharma', 'Male', 'Grade 10', 'Section A', 'North Wing', 'Sanjay Sharma', 'Father', '+91 98765 11001', '+91 98765 11002', '120', '15'])
    writer.writerow(['Ananya Gupta', 'Female', 'Grade 9', 'Section B', 'East Gables', 'Rajesh Gupta', 'Father', '+91 98765 11003', '+91 98765 11004', '150', '20'])
    writer.writerow(['Rohan Mehta', 'Male', 'Grade 11', 'Section A', 'West Wing', 'Sunil Mehta', 'Father', '+91 98765 11005', '+91 98765 11006', '120', '15'])
    return response


def bulk_upload_students(request):
    """
    School Admin: Bulk Student Excel/CSV Upload.
    Validate excel records and import students.
    """
    school = get_current_school(request)
    upload_result = None

    if request.method == "POST" and (request.FILES.get('spreadsheet') or request.FILES.get('file')):
        uploaded_file = request.FILES.get('spreadsheet') or request.FILES.get('file')
        filename = uploaded_file.name

        try:
            decoded_file = uploaded_file.read().decode('utf-8-sig')
            reader = csv.DictReader(io.StringIO(decoded_file))

            valid_rows = []
            error_rows = []
            row_idx = 1

            for row in reader:
                row_idx += 1
                name = row.get('student_full_name') or row.get('Name') or ''
                class_name = row.get('class_grade') or row.get('Class') or 'Grade 10'
                section = row.get('section') or row.get('Section') or 'Section A'
                phone = row.get('father_authorized_phone') or row.get('Primary Phone') or ''
                guardian = row.get('guardian_name') or 'Parent / Guardian'
                relation = row.get('relation') or 'Father'
                gender = row.get('gender') or 'Male'
                hostel = row.get('hostel_wing') or 'Boarding Wing'
                minutes = int(row.get('allocated_minutes') or 120)

                # field validation
                if not name.strip():
                    error_rows.append({"row": row_idx, "name": name, "reason": "Missing mandatory student name"})
                    continue
                if not phone.strip():
                    error_rows.append({"row": row_idx, "name": name, "reason": "Missing mandatory authorized phone"})
                    continue

                # Duplicate detection check
                if Student.objects.filter(school=school, name__iexact=name.strip(), primary_phone=phone.strip()).exists():
                    error_rows.append({"row": row_idx, "name": name, "reason": f"Duplicate record: {name} with phone {phone} already exists"})
                    continue

                valid_rows.append({
                    "name": name.strip(),
                    "class_name": class_name.strip(),
                    "section": section.strip(),
                    "phone": phone.strip(),
                    "guardian": guardian.strip(),
                    "relation": relation.strip(),
                    "gender": gender.strip(),
                    "hostel": hostel.strip(),
                    "minutes": minutes,
                })

            # Process valid rows atomically
            with transaction.atomic():
                imported_count = 0
                for item in valid_rows:
                    total_count = Student.objects.count() + imported_count + 1
                    s_code = f"STU-{total_count + 4000}"
                    c_code = f"S2D-{school.code[:3] if school else 'SCH'}-{random.randint(1000, 9999)}"

                    stu = Student.objects.create(
                        school=school,
                        code=s_code,
                        calling_code=c_code,
                        name=item['name'],
                        gender=item['gender'],
                        class_name=item['class_name'],
                        section=item['section'],
                        hostel_wing=item['hostel'],
                        guardian_name=item['guardian'],
                        guardian_relation=item['relation'],
                        primary_phone=item['phone'],
                        remaining_minutes=item['minutes'],
                        daily_limit_min=school.daily_duration_cap if school else 15,
                        status='Active'
                    )

                    Guardian.objects.create(
                        school=school,
                        student=stu,
                        code=f"GRD-{Guardian.objects.count() + 501}",
                        name=item['guardian'],
                        relation=item['relation'],
                        father_phone=item['phone'],
                        whitelist_status="Authorized (1 Number)",
                        status='Active'
                    )
                    imported_count += 1

            upload_result = {
                "filename": filename,
                "total_rows": row_idx - 1,
                "imported_count": len(valid_rows),
                "error_count": len(error_rows),
                "errors": error_rows,
            }
        except Exception as e:
            upload_result = {
                "filename": filename,
                "total_rows": 0,
                "imported_count": 0,
                "error_count": 1,
                "errors": [{"row": 0, "name": "File", "reason": f"Failed to parse CSV: {str(e)}"}]
            }

    context = {
        "school": school,
        "upload_result": upload_result,
    }
    return render(request, 'school-admin/bulk-upload/index.html', context)


# --- 4. CLASS & SECTION MANAGEMENT ---
def classes_list(request):
    """Dynamic School Admin Academic Classes Management."""
    school = get_current_school(request)

    if request.method == "POST":
        action = request.POST.get('action')
        if action == 'edit':
            cls_code = request.POST.get('class_code') or request.POST.get('code')
            c = AcademicClass.objects.filter(Q(code=cls_code) | Q(name=request.POST.get('original_name')), school=school).first()
            if c:
                if request.POST.get('className') or request.POST.get('name'):
                    c.name = (request.POST.get('className') or request.POST.get('name')).strip()
                if request.POST.get('supervisor'):
                    c.supervisor = request.POST.get('supervisor').strip()
                if request.POST.get('defaultDailyMinutes') or request.POST.get('default_daily_minutes'):
                    c.default_daily_minutes = int(request.POST.get('defaultDailyMinutes') or request.POST.get('default_daily_minutes'))
                if request.POST.get('schedule_group'):
                    c.schedule_group = request.POST.get('schedule_group')
                if request.POST.get('status'):
                    c.status = request.POST.get('status')
                c.save()
            return redirect('/school-admin/classes/list.html')
        elif action in ['delete', 'archive']:
            cls_code = request.POST.get('class_code') or request.POST.get('code')
            c = AcademicClass.objects.filter(Q(code=cls_code) | Q(name=cls_code), school=school).first()
            if c:
                c.status = 'Archived'
                c.save(update_fields=['status'])
            return redirect('/school-admin/classes/list.html')

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
        action = request.POST.get('action')
        if action == 'edit':
            sec_code = request.POST.get('section_code') or request.POST.get('code')
            s = ClassSection.objects.filter(code=sec_code, school=school).first()
            if s:
                if request.POST.get('sectionName'):
                    s.name = request.POST.get('sectionName').strip()
                if request.POST.get('roomWing'):
                    s.room_wing = request.POST.get('roomWing').strip()
                if request.POST.get('advisor'):
                    s.advisor = request.POST.get('advisor').strip()
                if request.POST.get('assignedBooth'):
                    s.assigned_booth = request.POST.get('assignedBooth').strip()
                if request.POST.get('status'):
                    s.status = request.POST.get('status')
                s.save()
            return redirect('/school-admin/classes/sections.html')
        elif action in ['delete', 'archive']:
            sec_code = request.POST.get('section_code') or request.POST.get('code')
            s = ClassSection.objects.filter(code=sec_code, school=school).first()
            if s:
                s.status = 'Archived'
                s.save(update_fields=['status'])
            return redirect('/school-admin/classes/sections.html')

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


# --- 5. PARENTS & GUARDIANS WHITELIST MANAGEMENT ---
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
    school = get_current_school(request)
    guardian_id = request.GET.get('id')
    guardian = Guardian.objects.filter(
        Q(code=guardian_id) | Q(id=guardian_id if str(guardian_id).isdigit() else 0)
    ).select_related('student', 'school').first()
    if not guardian:
        guardian = Guardian.objects.filter(school=school).select_related('student', 'school').first() or Guardian.objects.select_related('student', 'school').first()

    calls_qs = CallRecord.objects.none()
    if guardian:
        phones = [p for p in [guardian.father_phone, guardian.mother_phone, guardian.emergency_phone] if p]
        q_filter = Q(guardian=guardian)
        if phones:
            q_filter |= Q(destination_number__in=phones)
        calls_qs = CallRecord.objects.filter(q_filter).select_related('student', 'guardian', 'school').order_by('-start_time')[:20]

    call_history_data = [
        {
            "id": c.call_id,
            "studentName": c.student.name if c.student else "Student",
            "studentCode": c.student.calling_code if c.student else "N/A",
            "school": c.school.name if c.school else "",
            "authorizedNumber": c.destination_number,
            "guardianName": guardian.name if guardian else c.call_type,
            "startTime": c.start_time.strftime("%Y-%m-%d %H:%M"),
            "duration": f"{c.duration_seconds // 60}m {c.duration_seconds % 60:02d}s" if c.duration_seconds > 0 else "0m 00s",
            "minutesUsed": c.minutes_deducted,
            "status": c.call_status,
            "dateOnly": c.start_time.strftime("%Y-%m-%d"),
            "recordingUrl": c.audio_recording_url,
        }
        for c in calls_qs
    ]

    context = {
        "guardian": guardian,
        "student": guardian.student if guardian else None,
        "call_history_json": json.dumps(call_history_data),
        "school": guardian.school if guardian else school,
    }
    return render(request, 'school-admin/guardians/details.html', context)


def guardian_edit(request):
    """School Admin: Modify authorized phone numbers or pause dialer authorization."""
    guardian_id = request.GET.get('id')
    guardian = Guardian.objects.filter(Q(code=guardian_id) | Q(id=guardian_id if str(guardian_id).isdigit() else 0)).select_related('student', 'school').first()
    if not guardian:
        guardian = Guardian.objects.first()

    if request.method == "POST" and guardian:
        guardian.name = request.POST.get('name', guardian.name).strip()
        guardian.email = request.POST.get('email', guardian.email).strip()
        if 'relation' in request.POST:
            guardian.relation = request.POST.get('relation')
        guardian.father_phone = (request.POST.get('fatherPhone') or request.POST.get('father_phone', guardian.father_phone)).strip()
        guardian.mother_phone = (request.POST.get('motherPhone') or request.POST.get('mother_phone', guardian.mother_phone)).strip()
        if request.POST.get('emergencyPhone') or request.POST.get('emergency_phone'):
            guardian.emergency_phone = (request.POST.get('emergencyPhone') or request.POST.get('emergency_phone')).strip()
        if 'status' in request.POST:
            guardian.status = request.POST.get('status')

        active_numbers = [p for p in [guardian.father_phone, guardian.mother_phone, guardian.emergency_phone] if p and p != 'N/A']
        guardian.whitelist_status = f"Authorized ({len(active_numbers)} Number{'s' if len(active_numbers) != 1 else ''})"
        guardian.save()

        # Update student primary_phone and guardian_name as well
        if guardian.student:
            if guardian.father_phone:
                guardian.student.primary_phone = guardian.father_phone
            if guardian.name:
                guardian.student.guardian_name = guardian.name
            if guardian.mother_phone:
                guardian.student.secondary_phone = guardian.mother_phone
            guardian.student.save(update_fields=['primary_phone', 'guardian_name', 'secondary_phone'])

        return redirect(f"/school-admin/guardians/details.html?id={guardian.code}")

    context = {
        "guardian": guardian,
        "student": guardian.student if guardian else None,
        "school": guardian.school if guardian else get_current_school(request),
    }
    return render(request, 'school-admin/guardians/edit.html', context)


# --- 6. STUDENT UNIQUE CODES & AUTHENTICATION ENGINE ---
def student_codes(request):
    """
    School Admin: Unique Student Calling Codes Management.
    Atomically generates, rotates, and assigns collision-free kiosk login codes.
    """
    school = get_current_school(request)
    students = Student.objects.filter(school=school).order_by('name')

    issued_info = None

    if request.method == "POST":
        data = {}
        if request.body:
            try:
                data = json.loads(request.body.decode('utf-8'))
            except Exception:
                pass
        if not data:
            data = request.POST.dict()

        student_id = data.get('student_id') or request.POST.get('student_id')
        pin_policy = data.get('pin_policy') or request.POST.get('pin_policy', 'Unique Code + 4-Digit Student PIN')
        action = data.get('action') or request.POST.get('action', 'issue')

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

        is_ajax = (
            request.headers.get('x-requested-with') == 'XMLHttpRequest' or
            (request.content_type and 'application/json' in request.content_type) or
            bool(request.body and data.get('ajax'))
        )
        if is_ajax:
            return JsonResponse({
                "status": "success",
                "action": action,
                "student_code": student.code if student else None,
                "calling_code": student.calling_code if student else None,
                "code_status": student.code_status if student else None,
                "pin_policy": student.pin_policy if student else None,
                "issued_info": issued_info
            })

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

    issued_codes = [
        {
            "student_name": s.name,
            "student_code": s.code,
            "class_name": s.class_name,
            "section": s.section,
            "code": s.calling_code,
            "pin_policy": s.pin_policy,
            "status": s.code_status,
            "issued_at": s.code_issued_at,
            "last_used": s.code_last_used,
        }
        for s in students if s.calling_code
    ]

    context = {
        "school": school,
        "students": students,
        "issued_codes": issued_codes,
        "student_codes_json": json.dumps(student_codes_data),
        "issued_info": issued_info,
        "total_codes": len(issued_codes),
        "active_codes": students.filter(code_status='Active').count(),
        "suspended_codes": students.filter(code_status='Suspended').count(),
    }
    return render(request, 'school-admin/student-codes/index.html', context)


# --- 7. STUDENT ACTIVATION / DEACTIVATION & AUDIT LOGS ---
def student_status(request):
    """
    School Admin: Student Account Lifecycle & Activation / Deactivation.
    Handles activation, temporary suspension, disciplinary holds, batch updates, and audit logging.
    """
    school = get_current_school(request)
    students = Student.objects.filter(school=school).order_by('name')

    status_message = None

    if request.method == "POST":
        data = {}
        if request.body:
            try:
                data = json.loads(request.body.decode('utf-8'))
            except Exception:
                pass
        if not data:
            data = request.POST.dict()

        student_ids = data.get('student_ids') or request.POST.getlist('student_ids')
        student_id = data.get('student_id') or request.POST.get('student_id')
        new_status = (data.get('status') or request.POST.get('status') or 'Active').strip()
        reason = (data.get('reason') or request.POST.get('reason') or 'Administrative status review').strip()
        authorized_by = (
            data.get('authorized_by')
            or request.POST.get('authorized_by')
            or (request.user.get_full_name() if getattr(request, 'user', None) and request.user.is_authenticated and request.user.get_full_name() else 'School Administrator')
        ).strip()

        target_ids = []
        if isinstance(student_ids, list) and student_ids:
            target_ids = [str(sid).strip() for sid in student_ids if str(sid).strip()]
        elif student_ids and isinstance(student_ids, str):
            target_ids = [s.strip() for s in student_ids.split(',') if s.strip()]
        elif student_id:
            target_ids = [str(student_id).strip()]

        updated_count = 0
        last_student_name = ""
        last_prev_status = ""

        if target_ids and new_status in ['Active', 'Inactive', 'Suspended']:
            with transaction.atomic():
                for sid in target_ids:
                    s = Student.objects.filter(
                        Q(code=sid) | Q(calling_code=sid) | Q(id=sid if str(sid).isdigit() else 0),
                        school=school
                    ).first()
                    if s:
                        prev = s.status
                        s.status = new_status
                        if new_status == 'Suspended':
                            s.code_status = 'Suspended'
                        elif new_status == 'Active':
                            s.code_status = 'Active'
                        s.save(update_fields=['status', 'code_status'])

                        StudentStatusLog.objects.create(
                            student=s,
                            school=school,
                            previous_status=prev,
                            new_status=new_status,
                            reason=reason,
                            authorized_by=authorized_by
                        )
                        updated_count += 1
                        last_student_name = s.name
                        last_prev_status = prev

        if updated_count == 1:
            status_message = f"Status for {last_student_name} transitioned from {last_prev_status} to {new_status}."
        elif updated_count > 1:
            status_message = f"Successfully updated status to {new_status} for {updated_count} students."

        is_ajax = (
            request.headers.get('x-requested-with') == 'XMLHttpRequest'
            or 'application/json' in request.headers.get('accept', '')
            or request.content_type == 'application/json'
        )
        if is_ajax:
            return JsonResponse({
                "status": "success",
                "message": status_message or "Account status updated in database.",
                "updated_count": updated_count,
                "new_status": new_status,
                "active_count": Student.objects.filter(school=school, status='Active').count(),
                "inactive_count": Student.objects.filter(school=school, status='Inactive').count(),
                "suspended_count": Student.objects.filter(school=school, status='Suspended').count()
            })

    status_logs = StudentStatusLog.objects.filter(school=school).select_related('student').order_by('-timestamp')[:50]

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


# --- 8. CALLING DURATION RULES & LIMITS ---
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


# --- 9. CALLING SCHEDULES & EXCEPTION WINDOWS ---
def calling_schedules(request):
    """School Admin: School, class, and student-wise calling schedules and exception windows."""
    school = get_current_school(request)

    if request.method == "POST":
        action = request.POST.get('action')
        if action == 'publish_schedule':
            # update calling schedule rules
            rule, _ = CallingScheduleRule.objects.get_or_create(
                school=school,
                scope="School-Wide Standard",
                defaults={"allowed_window": "07:00 – 08:00, 17:30 – 21:00", "status": "Active"}
            )
            rule.status = 'Active'
            rule.save()
            return redirect('/school-admin/calling-schedules/index.html')

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


# --- 10. STUDENT VALIDITY DESK & MANUAL EXTENSIONS ---
def validity_overview(request):
    """
    School Admin: Student account validity & expiring accounts monitoring.
    Manage student validity extensions.
    """
    school = get_current_school(request)

    # manual validity extension
    if request.method == "POST":
        action = request.POST.get('action')
        if action == 'extend_validity':
            student_id = request.POST.get('student_id')
            days = int(request.POST.get('days_to_extend', 30))
            reason = request.POST.get('reason', 'Campus administrative validity extension')

            student = Student.objects.filter(
                Q(code=student_id) | Q(calling_code=student_id) | Q(id=student_id if str(student_id).isdigit() else 0),
                school=school
            ).first()

            if student:
                current_expiry = student.validity_expiry or timezone.now().date()
                student.validity_expiry = current_expiry + timedelta(days=days)
                student.validity_status = 'Active'
                student.save()

                ValidityExtensionLog.objects.create(
                    school=school,
                    student=student,
                    days_extended=days,
                    reason=reason
                )
            return redirect('/school-admin/validity/index.html')

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


# --- 11. RECHARGES MANAGEMENT & FINANCIAL LEDGER ---
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


# --- 12. CALL HISTORY & TELEMETRY LOGS ---
def call_history(request):
    """
    School Admin: Campus Call History & Telemetry Log.
    Search call records by student, date, or number.
    """
    school = get_current_school(request)
    calls_qs = CallRecord.objects.filter(school=school).select_related('student', 'guardian').order_by('-start_time')

    q = request.GET.get('q', '').strip()
    if q:
        calls_qs = calls_qs.filter(
            Q(call_id__icontains=q) |
            Q(student__name__icontains=q) |
            Q(student__calling_code__icontains=q) |
            Q(destination_number__icontains=q) |
            Q(guardian__name__icontains=q)
        )

    status_filter = request.GET.get('status', '').strip()
    if status_filter:
        calls_qs = calls_qs.filter(call_status=status_filter)

    date_filter = request.GET.get('date', '').strip()
    if date_filter:
        calls_qs = calls_qs.filter(start_time__date=date_filter)

    total_calls = calls_qs.count()
    completed_calls = calls_qs.filter(call_status='Completed').count()
    restricted_calls = calls_qs.filter(call_status='Restricted Schedule').count()
    total_minutes = calls_qs.aggregate(total=Sum('minutes_deducted'))['total'] or 0

    call_records_data = [
        {
            "id": c.call_id,
            "studentName": c.student.name if c.student else "Student",
            "studentCode": c.student.calling_code if c.student else "N/A",
            "school": school.name,
            "authorizedNumber": c.destination_number,
            "guardianName": c.guardian.name if c.guardian else c.call_type,
            "startTime": c.start_time.strftime("%Y-%m-%d %H:%M"),
            "duration": f"{c.duration_seconds // 60}m {c.duration_seconds % 60:02d}s" if c.duration_seconds > 0 else "0m 00s",
            "minutesUsed": c.minutes_deducted,
            "status": c.call_status,
            "dateOnly": c.start_time.strftime("%Y-%m-%d"),
            "recordingUrl": c.audio_recording_url,
        }
        for c in calls_qs[:100]
    ]

    context = {
        "school": school,
        "call_records": calls_qs[:100],
        "call_history_json": json.dumps(call_records_data),
        "total_calls": total_calls,
        "completed_calls": completed_calls,
        "restricted_calls": restricted_calls,
        "flagged_calls": restricted_calls,
        "total_minutes": total_minutes,
        "total_duration_minutes": total_minutes,
        "q": q,
        "status_filter": status_filter,
    }
    return render(request, 'school-admin/call-history/index.html', context)


# --- 13. HOSTEL WARDENS MANAGEMENT ---
def hostel_wardens_list(request):
    """
    School Admin: Hostel Warden Directory & Duty Roster.
    Add or update hostel warden assignment.
    """
    school = get_current_school(request)
    wardens_qs = HostelWarden.objects.filter(school=school).order_by('name')

    on_duty_count = wardens_qs.filter(status='On Duty').count()
    total_booths_covered = sum(w.booths_monitored for w in wardens_qs)

    wardens_data = [
        {
            "id": w.code,
            "name": w.name,
            "email": w.email or f"{w.name.lower().replace(' ', '.')}@doonvalley.edu.in",
            "phone": w.phone,
            "hostelWing": w.hostel_block,
            "shiftHours": w.shift_timings,
            "supervisedStudents": 45,
            "supervisedDevices": w.booths_monitored,
            "emergencyOverride": "Authorized",
            "status": "Active" if w.status == "On Duty" else "Inactive",
            "rawStatus": w.status,
        }
        for w in wardens_qs
    ]

    context = {
        "school": school,
        "wardens": wardens_qs,
        "wardens_json": json.dumps(wardens_data),
        "on_duty_count": on_duty_count,
        "total_booths_covered": total_booths_covered,
    }
    return render(request, 'school-admin/hostel-wardens/list.html', context)


def hostel_warden_add(request):
    """Register new duty warden."""
    school = get_current_school(request)
    if request.method == "POST":
        name = request.POST.get('name', '').strip()
        phone = request.POST.get('phone', '').strip()
        email = request.POST.get('email', '').strip()
        hostel_block = request.POST.get('hostel_block', 'North Hall').strip()
        shift = request.POST.get('shift_timings', '16:00 – 00:00').strip()
        booths = int(request.POST.get('booths_monitored', 4))
        status = request.POST.get('status', 'On Duty')

        code = f"WRD-{HostelWarden.objects.filter(school=school).count() + 101}"
        HostelWarden.objects.create(
            school=school,
            code=code,
            name=name,
            phone=phone,
            email=email,
            hostel_block=hostel_block,
            shift_timings=shift,
            booths_monitored=booths,
            status=status
        )
        return redirect('/school-admin/hostel-wardens/list.html')
    return render(request, 'school-admin/hostel-wardens/add.html', {"school": school})


def hostel_warden_edit(request):
    """Edit warden records."""
    warden_id = request.GET.get('id')
    warden = HostelWarden.objects.filter(Q(code=warden_id) | Q(id=warden_id if str(warden_id).isdigit() else 0)).first()
    if not warden:
        warden = HostelWarden.objects.first()

    if request.method == "POST" and warden:
        warden.name = request.POST.get('name', warden.name).strip()
        warden.phone = request.POST.get('phone', warden.phone).strip()
        warden.email = request.POST.get('email', warden.email).strip()
        warden.hostel_block = request.POST.get('hostel_block', warden.hostel_block).strip()
        warden.shift_timings = request.POST.get('shift_timings', warden.shift_timings).strip()
        if request.POST.get('booths_monitored'):
            try:
                warden.booths_monitored = int(request.POST['booths_monitored'])
            except ValueError:
                pass
        warden.status = request.POST.get('status', warden.status)
        warden.save()
        return redirect('/school-admin/hostel-wardens/list.html')

    return render(request, 'school-admin/hostel-wardens/edit.html', {"warden": warden, "school": warden.school if warden else None})


def hostel_warden_details(request):
    """View warden shift record and supervised kiosk devices."""
    school = get_current_school(request)
    warden_id = request.GET.get('id')
    warden = HostelWarden.objects.filter(
        Q(code=warden_id) | Q(id=warden_id if str(warden_id).isdigit() else 0)
    ).select_related('school').first()
    if not warden:
        warden = HostelWarden.objects.filter(school=school).select_related('school').first() or HostelWarden.objects.select_related('school').first()

    target_school = warden.school if warden else school
    devices_qs = KioskDevice.objects.filter(school=target_school) if target_school else KioskDevice.objects.none()
    if warden and warden.hostel_block:
        block_devices = devices_qs.filter(hostel_block__icontains=warden.hostel_block)
        if block_devices.exists():
            devices_qs = block_devices

    devices_data = [
        {
            "id": d.device_id,
            "deviceName": d.name,
            "model": d.app_version,
            "schoolId": target_school.code if target_school else "",
            "wingLocation": d.hostel_block,
            "assignedMode": d.assigned_wing or "Hostel Wing Booth",
            "enrollmentStatus": "Enrolled",
            "onlineStatus": d.status,
            "lastHeartbeat": d.last_heartbeat.strftime("%H:%M Today") if d.last_heartbeat else "Just now",
            "status": "Active" if d.status == "Online" else "Available",
        }
        for d in devices_qs
    ]

    context = {
        "warden": warden,
        "school": target_school,
        "devices_json": json.dumps(devices_data),
    }
    return render(request, 'school-admin/hostel-wardens/details.html', context)


# --- 14. DEVICE ASSIGNMENT MANAGEMENT ---
def device_assignments_list(request):
    """
    School Admin: Calling Booths & Device Assignments.
    """
    school = get_current_school(request)
    devices = KioskDevice.objects.filter(school=school).select_related('assigned_student').order_by('name') if school else KioskDevice.objects.none()
    assignments = DeviceAssignment.objects.filter(school=school).select_related('device', 'student') if school else DeviceAssignment.objects.none()

    online_count = devices.filter(status='Online').count()
    offline_count = devices.filter(status='Offline').count()
    delayed_count = devices.filter(status='Maintenance').count()

    devices_data = []
    for d in devices:
        if d.assigned_student:
            assigned_mode = f"Student: {d.assigned_student.name} ({d.assigned_student.code})"
            assignment_badge = "Active (1-to-1)"
        elif d.assigned_wing:
            assigned_mode = f"Wing: {d.assigned_wing} ({d.hostel_block})"
            assignment_badge = "Active (Booth)"
        else:
            assigned_mode = "Unassigned / Available"
            assignment_badge = "Available"

        devices_data.append({
            "id": d.device_id,
            "deviceName": d.name,
            "model": d.app_version,
            "schoolId": school.code if school else "",
            "wingLocation": d.hostel_block,
            "assignedMode": assigned_mode,
            "enrollmentStatus": "Enrolled",
            "onlineStatus": d.status,
            "lastHeartbeat": d.last_heartbeat.strftime("%H:%M Today") if d.last_heartbeat else "Just now",
            "status": "Active" if (d.assigned_student or d.assigned_wing) else "Available",
            "assignedStudentId": d.assigned_student.id if d.assigned_student else None,
            "assignedStudentCode": d.assigned_student.code if d.assigned_student else "",
            "assignedStudentName": d.assigned_student.name if d.assigned_student else "",
            "assignmentType": d.assignment_type,
            "isAssigned": bool(d.assigned_student or d.assigned_wing),
        })

    context = {
        "school": school,
        "devices": devices,
        "assignments": assignments,
        "devices_json": json.dumps(devices_data),
        "online_count": online_count,
        "offline_count": offline_count,
        "delayed_count": delayed_count,
    }
    return render(request, 'school-admin/device-assignments/list.html', context)


def device_assign(request):
    """
    School Admin: Assign Device to Student or Wing.
    Assign enrolled kiosk device to student.
    """
    school = get_current_school(request)
    devices = (
        KioskDevice.objects.filter(Q(school=school) | Q(school__isnull=True))
        .select_related('assigned_student')
        .order_by('assigned_student__id', 'name')
    ) if school else KioskDevice.objects.none()
    students = Student.objects.filter(school=school, status='Active').order_by('name') if school else Student.objects.none()
    classes = AcademicClass.objects.filter(school=school).order_by('name') if school else AcademicClass.objects.none()
    wardens = HostelWarden.objects.filter(school=school).order_by('name') if school else HostelWarden.objects.none()

    error = None
    preselected_device = (request.GET.get('device') or request.POST.get('device_id') or '').strip()

    if request.method == "POST":
        device_id = (request.POST.get('device_id') or '').strip()
        device = KioskDevice.objects.filter(
            (Q(device_id=device_id) | (Q(id=int(device_id)) if str(device_id).isdigit() else Q())),
            Q(school=school) | Q(school__isnull=True)
        ).first()

        if not device:
            error = "Device is not enrolled in MDM or does not exist for this campus."
        elif device.status == 'Offline':
            error = "Device is currently Offline. Please ensure kiosk heartbeat is restored before assignment."
        else:
            mode_param = (request.POST.get('assignment_mode') or '').strip()
            student_id = (request.POST.get('student_id') or '').strip()
            if mode_param == 'Wing' or (not mode_param and not student_id and (request.POST.get('hostel_wing') or request.POST.get('academic_class'))):
                assignment_mode = 'Wing'
            else:
                assignment_mode = 'Student'

            assigned_by = (
                request.user.get_full_name()
                if getattr(request, 'user', None) and request.user.is_authenticated and request.user.get_full_name()
                else "Campus Admin"
            )

            if assignment_mode == 'Student':
                student = Student.objects.filter(
                    (Q(id=int(student_id)) if str(student_id).isdigit() else Q()) | Q(code=student_id) | Q(calling_code=student_id),
                    school=school
                ).first() if student_id else None
                if not student:
                    error = "Please select a valid active student to assign this device to."
                elif device.assigned_student and device.assigned_student.id != student.id:
                    error = f"Device {device.device_id} is already assigned to student {device.assigned_student.name} ({device.assigned_student.code}). Please unbind it first."
                else:
                    # 1-to-1 Device Policy: Clear any previous device assigned to this student
                    KioskDevice.objects.filter(school=school, assigned_student=student).exclude(id=device.id).update(assigned_student=None)

                    device.assigned_student = student
                    device.assignment_type = 'Student'
                    if student.hostel_wing:
                        device.hostel_block = student.hostel_wing
                    device.save(update_fields=['assigned_student', 'assignment_type', 'hostel_block'])

                    DeviceAssignment.objects.create(
                        school=school,
                        device=device,
                        student=student,
                        assignment_type='Student',
                        academic_class=student.class_name,
                        hostel_wing=student.hostel_wing or "Boarding Wing",
                        assigned_by=assigned_by,
                        status='Active'
                    )
                    is_ajax = (
                        request.headers.get('x-requested-with') == 'XMLHttpRequest'
                        or 'application/json' in request.headers.get('accept', '')
                        or request.content_type == 'application/json'
                    )
                    if is_ajax:
                        return JsonResponse({"status": "success", "message": f"Device {device.device_id} bound to student {student.name}.", "device_id": device.device_id})
                    return redirect('/school-admin/device-assignments/list.html?assigned=1')
            else:
                # Shared Hostel Wing Mode
                hostel_wing = (request.POST.get('hostel_wing') or 'Tagore Bhavan').strip()
                academic_class = (request.POST.get('academic_class') or 'All Classes').strip()

                device.assigned_student = None
                device.assignment_type = 'Wing'
                device.hostel_block = hostel_wing
                device.assigned_wing = academic_class
                device.save(update_fields=['assigned_student', 'assignment_type', 'hostel_block', 'assigned_wing'])

                DeviceAssignment.objects.create(
                    school=school,
                    device=device,
                    student=None,
                    assignment_type='Wing',
                    hostel_wing=hostel_wing,
                    academic_class=academic_class,
                    assigned_by=assigned_by,
                    status='Active'
                )
                is_ajax = (
                    request.headers.get('x-requested-with') == 'XMLHttpRequest'
                    or 'application/json' in request.headers.get('accept', '')
                    or request.content_type == 'application/json'
                )
                if is_ajax:
                    return JsonResponse({"status": "success", "message": f"Device {device.device_id} assigned to {hostel_wing}.", "device_id": device.device_id})
                return redirect('/school-admin/device-assignments/list.html?assigned=1')

    context = {
        "school": school,
        "devices": devices,
        "students": students,
        "classes": classes,
        "wardens": wardens,
        "preselected_device": preselected_device,
        "error": error,
    }
    return render(request, 'school-admin/device-assignments/assign.html', context)


def device_unassign(request):
    """
    School Admin: Unbind / Release Device from Student or Wing.
    Releases the hardware lock and marks device available.
    """
    school = get_current_school(request)
    device_id = (request.POST.get('device_id') or request.GET.get('device_id') or '').strip()
    if device_id and school:
        device = KioskDevice.objects.filter(
            (Q(device_id=device_id) | (Q(id=int(device_id)) if str(device_id).isdigit() else Q())),
            school=school
        ).first()
        if device:
            device.assigned_student = None
            device.assigned_wing = ""
            device.assignment_type = 'Student'
            device.save(update_fields=['assigned_student', 'assigned_wing', 'assignment_type'])
            DeviceAssignment.objects.filter(device=device, status='Active').update(status='Released')

    is_ajax = (
        request.headers.get('x-requested-with') == 'XMLHttpRequest'
        or 'application/json' in request.headers.get('accept', '')
        or request.content_type == 'application/json'
    )
    if is_ajax:
        return JsonResponse({"status": "success", "message": "Device unassigned and marked available."})
    return redirect('/school-admin/device-assignments/list.html?unassigned=1')


# --- 15. STUDENT & CLASS REPORTS (REPORTING ENGINE & CSV EXPORTS) ---
def student_reports(request):
    """
    School Admin: Student-wise calling usage and remaining duration reports.
    Generate usage and student reports.
    """
    school = get_current_school(request)
    students = Student.objects.filter(school=school).order_by('name') if school else Student.objects.none()
    classes = AcademicClass.objects.filter(school=school).order_by('name') if school else AcademicClass.objects.none()

    class_filter = request.GET.get('class')
    if class_filter:
        students = students.filter(class_name=class_filter)

    total_students = students.count()
    active_students = students.filter(status='Active').count()
    total_minutes = students.aggregate(total=Sum('remaining_minutes'))['total'] or 0
    avg_minutes = round(total_minutes / total_students) if total_students > 0 else 0

    students_data = [
        {
            "id": s.code,
            "code": s.code,
            "name": s.name,
            "studentCode": s.calling_code,
            "school": school.name if school else "",
            "className": s.class_name,
            "section": s.section,
            "hostelWing": s.hostel_wing or "Boarding Wing",
            "guardianName": s.guardian_name,
            "guardianRelation": s.guardian_relation,
            "primaryPhone": s.primary_phone,
            "remainingMinutes": s.remaining_minutes,
            "dailyLimitMin": s.daily_limit_min,
            "totalCalls": s.call_records.count(),
            "validityExpiry": s.validity_expiry.strftime("%Y-%m-%d") if s.validity_expiry else "2027-05-31",
            "status": s.status,
        }
        for s in students
    ]

    context = {
        "school": school,
        "students": students,
        "classes": classes,
        "total_students": total_students,
        "active_students": active_students,
        "total_minutes": total_minutes,
        "avg_minutes": avg_minutes,
        "students_json": json.dumps(students_data),
    }
    return render(request, 'school-admin/student-reports/index.html', context)


def export_student_reports_csv(request):
    """Export student reports to streaming CSV."""
    school = get_current_school(request)
    students = Student.objects.filter(school=school).order_by('name')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{school.code}_student_calling_reports.csv"'

    writer = csv.writer(response)
    writer.writerow(['Student Code', 'Name', 'Class', 'Section', 'Primary Guardian', 'Phone', 'Total Calls', 'Available Minutes', 'Validity Status', 'Status'])

    for s in students:
        writer.writerow([
            s.calling_code, s.name, s.class_name, s.section,
            s.guardian_name, s.primary_phone, s.call_records.count(),
            s.remaining_minutes, s.validity_status, s.status
        ])
    return response


def class_reports(request):
    """
    School Admin: Class-wise calling activity and duration breakdown.
    """
    school = get_current_school(request)
    classes = AcademicClass.objects.filter(school=school).order_by('name') if school else AcademicClass.objects.none()

    total_classes = classes.count()
    total_sections = ClassSection.objects.filter(school=school).count() if school else 0
    total_minutes = CallRecord.objects.filter(school=school).aggregate(total=Sum('minutes_deducted'))['total'] or 0 if school else 0

    classes_data = []
    usage_labels = []
    usage_minutes = []
    dist_active = []
    dist_inactive = []

    for c in classes:
        st_qs = Student.objects.filter(school=school, class_name__iexact=c.name)
        st_count = st_qs.count()
        act_count = st_qs.filter(status='Active').count()
        inact_count = st_count - act_count
        mins = CallRecord.objects.filter(
            school=school, student__class_name__iexact=c.name
        ).aggregate(total=Sum('minutes_deducted'))['total'] or 0

        classes_data.append({
            "id": c.code,
            "className": c.name,
            "supervisor": c.supervisor,
            "sectionsCount": c.sections.count(),
            "studentsCount": st_count,
            "activeCallers": act_count,
            "totalMinutesConsumed": int(mins),
        })
        usage_labels.append(c.name)
        usage_minutes.append(int(mins))
        dist_active.append(act_count)
        dist_inactive.append(inact_count)

    class_usage_chart = {
        "labels": usage_labels,
        "minutes": usage_minutes,
        "hasData": bool(usage_labels),
    }
    class_distribution_chart = {
        "labels": usage_labels,
        "active": dist_active,
        "inactive": dist_inactive,
        "hasData": bool(usage_labels),
    }

    context = {
        "school": school,
        "classes": classes,
        "total_classes": total_classes,
        "total_sections": total_sections,
        "total_minutes": total_minutes,
        "classes_json": json.dumps(classes_data),
        "class_usage_chart_json": json.dumps(class_usage_chart),
        "class_distribution_chart_json": json.dumps(class_distribution_chart),
    }
    return render(request, 'school-admin/class-reports/index.html', context)


def export_class_reports_csv(request):
    """Export class reports to streaming CSV."""
    school = get_current_school(request)
    classes = AcademicClass.objects.filter(school=school).order_by('name')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{school.code}_class_calling_reports.csv"'

    writer = csv.writer(response)
    writer.writerow(['Class Code', 'Class Name', 'Supervisor', 'Total Sections', 'Enrolled Students', 'Active Callers', 'Total Minutes Consumed'])

    for c in classes:
        st_count = Student.objects.filter(school=school, class_name__iexact=c.name).count()
        act_count = Student.objects.filter(school=school, class_name__iexact=c.name, status='Active').count()
        mins = CallRecord.objects.filter(school=school, student__class_name__iexact=c.name).aggregate(total=Sum('minutes_deducted'))['total'] or 0
        writer.writerow([c.code, c.name, c.supervisor, c.sections.count(), st_count, act_count, mins])
    return response


# --- 16. SCHOOL PROFILE & OPERATIONAL SETTINGS ---
def school_settings(request):
    """
    School Admin: Profile & Campus Operational Preferences (4 tabbed forms).
    Update school profile and settings.
    """
    school = get_current_school(request)

    status_message = None
    active_tab = request.GET.get('tab', 'profile')

    if request.method == "POST" and school:
        section = request.POST.get('settings_section', 'profile')
        active_tab = section

        if section == 'callerid':
            school.display_school_caller_id = request.POST.get('display_school_caller_id') == 'on'
            school.show_guardian_whitelist_numbers = request.POST.get('show_guardian_whitelist_numbers') == 'on'
            school.emergency_override_caller_id = request.POST.get('emergency_override_caller_id') == 'on'
            status_message = "Caller ID policies saved successfully."
        elif section == 'emergency':
            school.primary_emergency_phone = request.POST.get('primary_emergency_phone', school.primary_emergency_phone).strip()
            school.secondary_emergency_phone = request.POST.get('secondary_emergency_phone', school.secondary_emergency_phone).strip()
            school.warden_escalation_phone = request.POST.get('warden_escalation_phone', school.warden_escalation_phone).strip()
            status_message = "Emergency override contacts updated successfully."
        elif section == 'notify':
            school.notify_sms_guardians = request.POST.get('notify_sms_guardians') == 'on'
            school.notify_email_recharges = request.POST.get('notify_email_recharges') == 'on'
            school.notify_push_validity = request.POST.get('notify_push_validity') == 'on'
            status_message = "Notification channel preferences saved successfully."
        else:
            new_name = (request.POST.get('school_name') or request.POST.get('name') or school.name).strip()
            school.name = new_name
            school.admin_name = request.POST.get('admin_name', school.admin_name).strip()
            school.admin_email = request.POST.get('admin_email', school.admin_email).strip()
            school.admin_phone = request.POST.get('admin_phone', school.admin_phone).strip()
            if 'hostel_blocks_count' in request.POST and request.POST['hostel_blocks_count'].isdigit():
                school.hostel_blocks_count = int(request.POST['hostel_blocks_count'])
            if 'daily_duration_cap' in request.POST and request.POST['daily_duration_cap'].isdigit():
                school.daily_duration_cap = int(request.POST['daily_duration_cap'])
            if 'calling_window_start' in request.POST:
                school.calling_window_start = request.POST['calling_window_start']
            if 'calling_window_end' in request.POST:
                school.calling_window_end = request.POST['calling_window_end']
            status_message = "Campus identity & operational profile saved successfully."

        school.save()

    context = {
        "school": school,
        "message": status_message,
        "status_message": status_message,
        "active_tab": active_tab,
    }
    return render(request, 'school-admin/settings/index.html', context)


def _parse_school_post_data(request):
    data = {}
    if request.body:
        try:
            data = json.loads(request.body.decode('utf-8'))
        except Exception:
            pass
    if not data:
        data = request.POST.dict()
    return data


def device_toggle_status(request):
    """School / Super Admin: Block/Unblock or change status for KioskDevice."""
    if request.method != "POST":
        return JsonResponse({"error": "POST_REQUIRED"}, status=405)
    data = _parse_school_post_data(request)
    device_id = (data.get('device_id') or data.get('id') or '').strip()
    ids = data.get('ids') or []
    target_status = (data.get('status') or 'Active').strip()

    targets = [str(x).strip() for x in ids if str(x).strip()] if ids else ([device_id] if device_id else [])
    qs = KioskDevice.objects.filter(Q(device_id__in=targets) | Q(id__in=[int(x) for x in targets if x.isdigit()]))
    school = get_current_school(request)
    if school and not getattr(request.user, 'is_superuser', False):
        qs = qs.filter(school=school)

    updated = qs.update(status=target_status)
    return JsonResponse({
        "status": "success",
        "new_status": target_status,
        "count": updated
    })


def guardian_toggle_status(request):
    """School Admin: Revoke or restore authorization for guardian contact."""
    if request.method != "POST":
        return JsonResponse({"error": "POST_REQUIRED"}, status=405)
    data = _parse_school_post_data(request)
    guardian_id = (data.get('guardian_id') or data.get('id') or data.get('code') or '').strip()
    ids = data.get('ids') or []
    target_status = (data.get('status') or 'Active').strip()

    targets = [str(x).strip() for x in ids if str(x).strip()] if ids else ([guardian_id] if guardian_id else [])
    qs = Guardian.objects.filter(Q(code__in=targets) | Q(id__in=[int(x) for x in targets if x.isdigit()]))
    school = get_current_school(request)
    if school:
        qs = qs.filter(student__school=school)

    updated = qs.update(status=target_status)
    return JsonResponse({
        "status": "success",
        "new_status": target_status,
        "count": updated
    })


def warden_toggle_status(request):
    """School Admin: Mark hostel warden Active or Inactive."""
    if request.method != "POST":
        return JsonResponse({"error": "POST_REQUIRED"}, status=405)
    data = _parse_school_post_data(request)
    warden_id = (data.get('warden_id') or data.get('id') or data.get('code') or '').strip()
    ids = data.get('ids') or []
    target_status = (data.get('status') or 'Active').strip()

    targets = [str(x).strip() for x in ids if str(x).strip()] if ids else ([warden_id] if warden_id else [])
    qs = HostelWarden.objects.filter(Q(code__in=targets) | Q(id__in=[int(x) for x in targets if x.isdigit()]))
    school = get_current_school(request)
    if school:
        qs = qs.filter(school=school)

    updated = qs.update(status=target_status)
    return JsonResponse({
        "status": "success",
        "new_status": target_status,
        "count": updated
    })


def class_toggle_status(request):
    """School Admin: Activate or Archive academic class."""
    if request.method != "POST":
        return JsonResponse({"error": "POST_REQUIRED"}, status=405)
    data = _parse_school_post_data(request)
    class_id = (data.get('class_id') or data.get('id') or data.get('className') or '').strip()
    ids = data.get('ids') or []
    target_status = (data.get('status') or 'Active').strip()

    targets = [str(x).strip() for x in ids if str(x).strip()] if ids else ([class_id] if class_id else [])
    qs = AcademicClass.objects.filter(Q(code__in=targets) | Q(name__in=targets) | Q(id__in=[int(x) for x in targets if x.isdigit()]))
    school = get_current_school(request)
    if school:
        qs = qs.filter(school=school)

    updated = qs.update(status=target_status)
    return JsonResponse({
        "status": "success",
        "new_status": target_status,
        "count": updated
    })


def section_toggle_status(request):
    """School Admin: Activate or Archive class section."""
    if request.method != "POST":
        return JsonResponse({"error": "POST_REQUIRED"}, status=405)
    data = _parse_school_post_data(request)
    section_id = (data.get('section_id') or data.get('id') or data.get('code') or '').strip()
    ids = data.get('ids') or []
    target_status = (data.get('status') or 'Active').strip()

    targets = [str(x).strip() for x in ids if str(x).strip()] if ids else ([section_id] if section_id else [])
    qs = ClassSection.objects.filter(Q(code__in=targets) | Q(name__in=targets) | Q(id__in=[int(x) for x in targets if x.isdigit()]))
    school = get_current_school(request)
    if school:
        qs = qs.filter(academic_class__school=school)

    updated = qs.update(status=target_status)
    return JsonResponse({
        "status": "success",
        "new_status": target_status,
        "count": updated
    })


def validity_extend_student(request):
    """School Admin & Super Admin: Live student validity extension by N days."""
    if request.method != "POST":
        return JsonResponse({"error": "POST_REQUIRED"}, status=405)
    data = _parse_school_post_data(request)
    student_id = (data.get('student_id') or data.get('student_code') or data.get('id') or '').strip()
    days = int(data.get('days') or data.get('extension_days') or 90)
    reason = (data.get('reason') or f"Administrative +{days}d extension").strip()

    student = Student.objects.filter(
        Q(code=student_id) | Q(calling_code=student_id) | Q(id=int(student_id) if student_id.isdigit() else 0)
    ).first()
    if not student:
        return JsonResponse({"error": "STUDENT_NOT_FOUND", "message": f"Student '{student_id}' not found."}, status=404)

    today = timezone.now().date()
    base_date = student.validity_expiry if (student.validity_expiry and student.validity_expiry >= today) else today
    new_expiry = base_date + timedelta(days=days)

    student.validity_expiry = new_expiry
    if student.status == 'Suspended':
        student.status = 'Active'
    if student.code_status == 'Suspended':
        student.code_status = 'Active'
    student.save(update_fields=['validity_expiry', 'status', 'code_status'])

    ValidityExtensionLog.objects.create(
        school=student.school,
        target_type=f"Student {student.code}",
        days_extended=days,
        reason=reason
    )

    eval_res = ValidityService.evaluate(student)
    return JsonResponse({
        "status": "success",
        "student_code": student.code,
        "new_expiry": new_expiry.strftime("%Y-%m-%d"),
        "validity_status": eval_res["status"],
        "days_left": eval_res["days_left"],
        "message": f"Extended validity through {new_expiry}."
    })


# --- 17. SUBPAGE FALLBACK RENDERER ---
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
