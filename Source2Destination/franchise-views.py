"""
Franchise Partner Views Implementation Source (franchise-views.py)
Source 2 Destination — Regional Operations Portal
Primary implementation source per AGENTS.md guidelines.
"""
import os
from django.shortcuts import render, redirect
from django.http import Http404, HttpResponseBadRequest
from django.template.loader import get_template
from django.template import TemplateDoesNotExist
from django.db.models import Sum, Count, Q
from .models import School, Franchise, Student


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
    total_students = schools_qs.aggregate(total=Sum('enrolled_students'))['total'] or 0
    active_students = schools_qs.aggregate(total=Sum('active_students'))['total'] or 0

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
    schools_qs = School.objects.filter(franchise=franchise)
    total_campuses = schools_qs.count()
    active_campuses = schools_qs.filter(status='Active').count()
    total_students = schools_qs.aggregate(total=Sum('enrolled_students'))['total'] or 0

    context = {
        "franchise": franchise,
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
    students_qs = Student.objects.filter(school__franchise=franchise)
    total_students = students_qs.count()
    active_students = students_qs.filter(status='Active').count()

    context = {
        "franchise": franchise,
        "total_students": total_students,
        "active_students": active_students,
    }
    return render(request, 'franchise/students/list.html', context)


def render_franchise_page(request, path):
    """Render any Franchise subpage dynamically."""
    clean_path = os.path.normpath(path).replace('\\', '/').strip('/')
    if clean_path.startswith('..'):
        raise Http404("Invalid template path")

    candidates = [
        f"franchise/{clean_path}",
        f"franchise/{clean_path}.html",
    ]
    if not clean_path.endswith('.html'):
        candidates.append(f"franchise/{clean_path}/index.html")

    for template_name in candidates:
        try:
            get_template(template_name)
            return render(request, template_name)
        except TemplateDoesNotExist:
            continue

    raise Http404(f"Franchise template '{clean_path}' not found")
