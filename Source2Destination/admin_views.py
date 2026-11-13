"""
Super Admin Environment Views
Source 2 Destination — Global Governance Portal
Handles all Super Admin UI views, dynamic school management, and institutional KPI metrics.
"""
import os
from django.shortcuts import render, redirect
from django.http import Http404, HttpResponseBadRequest
from django.template.loader import get_template
from django.template import TemplateDoesNotExist
from django.db.models import Sum, Count, Q
from .models import School, Franchise


def dashboard(request):
    """Render Super Admin Primary Dashboard with live system metrics."""
    total_campuses = School.objects.count()
    active_campuses = School.objects.filter(status='Active').count()
    total_students = School.objects.aggregate(total=Sum('enrolled_students'))['total'] or 0
    active_students = School.objects.aggregate(total=Sum('active_students'))['total'] or 0
    franchises_count = Franchise.objects.filter(status='Active').count()

    context = {
        "total_campuses": total_campuses,
        "active_campuses": active_campuses,
        "total_students": total_students,
        "active_students": active_students,
        "franchises_count": franchises_count,
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

    context = {
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


def render_admin_page(request, path):
    """Render any other Super Admin subpage dynamically."""
    clean_path = os.path.normpath(path).replace('\\', '/').strip('/')
    if clean_path.startswith('..'):
        raise Http404("Invalid template path")

    candidates = [
        f"super-admin/{clean_path}",
        f"super-admin/{clean_path}.html",
    ]
    if not clean_path.endswith('.html'):
        candidates.append(f"super-admin/{clean_path}/index.html")

    for template_name in candidates:
        try:
            get_template(template_name)
            return render(request, template_name)
        except TemplateDoesNotExist:
            continue

    raise Http404(f"Super Admin template '{clean_path}' not found")
