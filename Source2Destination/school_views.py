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
from .models import School, Franchise, Student


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
