"""
Application URL Configuration
Routes split cleanly across Super Admin, Franchise, School Admin, and API modules per AGENTS.md.
"""
from django.urls import path, re_path
from . import views
from . import admin_views
from . import franchise_views
from . import school_views
from . import Api_views

app_name = 'source2destination'

urlpatterns = [
    # Root / Auth Portal
    path('', views.index, name='index'),

    # Super Admin School Management Specific Views
    path('super-admin/schools/', admin_views.schools_list, name='super_admin_schools_list'),
    path('super-admin/schools/list.html', admin_views.schools_list, name='super_admin_schools_list_html'),
    path('super-admin/schools/add.html', admin_views.school_add, name='super_admin_school_add'),
    path('super-admin/schools/edit.html', admin_views.school_edit, name='super_admin_school_edit'),
    path('super-admin/schools/details.html', admin_views.school_details, name='super_admin_school_details'),

    # Super Admin Dashboards & Subpages
    path('super-admin/', admin_views.dashboard, name='super_admin_dashboard'),
    path('super-admin/dashboard.html', admin_views.dashboard, name='super_admin_dashboard_html'),
    re_path(r'^super-admin/(?P<path>.+?)/?$', admin_views.render_admin_page, name='super_admin_page'),

    # Franchise Partner Environment
    path('franchise/', franchise_views.dashboard, name='franchise_dashboard'),
    path('franchise/dashboard.html', franchise_views.dashboard, name='franchise_dashboard_html'),
    path('franchise/schools/', franchise_views.schools_list, name='franchise_schools_list'),
    path('franchise/schools/list.html', franchise_views.schools_list, name='franchise_schools_list_html'),
    path('franchise/schools/add.html', franchise_views.school_add, name='franchise_school_add'),
    path('franchise/schools/details.html', franchise_views.school_details, name='franchise_school_details'),
    path('franchise/schools/edit.html', franchise_views.school_edit, name='franchise_school_edit'),
    path('franchise/students/', franchise_views.students_list, name='franchise_students_list'),
    path('franchise/students/list.html', franchise_views.students_list, name='franchise_students_list_html'),
    path('franchise/classes/', franchise_views.classes_list, name='franchise_classes_list'),
    path('franchise/classes/index.html', franchise_views.classes_list, name='franchise_classes_list_html'),
    re_path(r'^franchise/(?P<path>.+?)/?$', franchise_views.render_franchise_page, name='franchise_page'),

    # School Admin Environment
    path('school-admin/', school_views.dashboard, name='school_admin_dashboard'),
    path('school-admin/dashboard.html', school_views.dashboard, name='school_admin_dashboard_html'),
    path('school-admin/students/', school_views.students_list, name='school_admin_students_list'),
    path('school-admin/students/list.html', school_views.students_list, name='school_admin_students_list_html'),
    path('school-admin/students/add.html', school_views.student_add, name='school_admin_student_add'),
    path('school-admin/students/details.html', school_views.student_details, name='school_admin_student_details'),
    path('school-admin/students/edit.html', school_views.student_edit, name='school_admin_student_edit'),
    path('school-admin/classes/', school_views.classes_list, name='school_admin_classes_list'),
    path('school-admin/classes/list.html', school_views.classes_list, name='school_admin_classes_list_html'),
    path('school-admin/classes/sections.html', school_views.sections_list, name='school_admin_sections_list'),
    path('school-admin/guardians/', school_views.guardians_list, name='school_admin_guardians_list'),
    path('school-admin/guardians/list.html', school_views.guardians_list, name='school_admin_guardians_list_html'),
    path('school-admin/guardians/add.html', school_views.guardian_add, name='school_admin_guardian_add'),
    path('school-admin/guardians/details.html', school_views.guardian_details, name='school_admin_guardian_details'),
    path('school-admin/guardians/edit.html', school_views.guardian_edit, name='school_admin_guardian_edit'),
    path('school-admin/student-codes/', school_views.student_codes, name='school_admin_student_codes'),
    path('school-admin/student-codes/index.html', school_views.student_codes, name='school_admin_student_codes_html'),
    path('school-admin/student-status/', school_views.student_status, name='school_admin_student_status'),
    path('school-admin/student-status/index.html', school_views.student_status, name='school_admin_student_status_html'),
    re_path(r'^school-admin/(?P<path>.+?)/?$', school_views.render_school_page, name='school_admin_page'),

    # Student Kiosk Application & Telemetry Endpoints (Api_views.py)
    path('api/status/', Api_views.api_status, name='api_status'),
    path('api/whitelist/<str:student_id>/', Api_views.student_whitelist_check, name='api_whitelist_check'),
    path('api/kiosk/heartbeat/', Api_views.device_heartbeat, name='api_device_heartbeat'),

    # Fallback Template Router (for auth/, etc.)
    re_path(r'^(?!static/)(?P<path>.+?)/?$', views.render_template_page, name='render_page'),
]
