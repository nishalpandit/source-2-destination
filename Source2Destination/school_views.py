"""
School Admin Views (school_views.py)
Source 2 Destination — Campus & Hostel Operations Portal
Handles campus-level student management, call allowances, and hostel phone operations.
"""
import os
from django.shortcuts import render, redirect
from django.http import Http404, HttpResponseBadRequest
from django.template.loader import get_template
from django.template import TemplateDoesNotExist
from django.db.models import Sum, Count, Q
from .models import School, Franchise, Student, AcademicClass, ClassSection


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
    total_minutes = students_qs.aggregate(total=Sum('remaining_minutes'))['total'] or 0

    context = {
        "school": school,
        "total_students": total_students,
        "active_students": active_students,
        "total_minutes": total_minutes,
    }
    return render(request, 'school-admin/dashboard.html', context)


def students_list(request):
    """Dynamic campus student directory view."""
    school = get_current_school(request)
    students_qs = Student.objects.filter(school=school) if school else Student.objects.none()
    total_students = students_qs.count()
    active_students = students_qs.filter(status='Active').count()

    context = {
        "school": school,
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

    context = {
        "school": school,
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

    classes_qs = AcademicClass.objects.filter(school=school, status='Active')
    context = {
        "school": school,
        "classes": classes_qs,
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
    sections_qs = ClassSection.objects.filter(school=school, status='Active')

    context = {
        "school": school,
        "classes": classes_qs,
        "sections": sections_qs,
        "total_sections": sections_qs.count(),
    }
    return render(request, 'school-admin/classes/sections.html', context)


def render_school_page(request, path):
    """Render any School Admin subpage dynamically."""
    clean_path = os.path.normpath(path).replace('\\', '/').strip('/')
    if clean_path.startswith('..'):
        raise Http404("Invalid template path")

    candidates = [
        f"school-admin/{clean_path}",
        f"school-admin/{clean_path}.html",
    ]
    if not clean_path.endswith('.html'):
        candidates.append(f"school-admin/{clean_path}/index.html")

    for template_name in candidates:
        try:
            get_template(template_name)
            return render(request, template_name)
        except TemplateDoesNotExist:
            continue

    raise Http404(f"School Admin template '{clean_path}' not found")
