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
    # Root / Unified Authentication Portal (Single Login Page)
    path('', views.login_view, name='login'),
    path('index.html', views.login_view, name='index_html'),
    path('login/', views.login_view, name='login_direct'),
    path('auth/login.html', views.login_view, name='auth_login_html'),
    path('logout/', views.logout_view, name='logout'),
    path('auth/logout/', views.logout_view, name='auth_logout'),

    # Super Admin School Management Specific Views
    path('super-admin/schools/', admin_views.schools_list, name='super_admin_schools_list'),
    path('super-admin/schools/list.html', admin_views.schools_list, name='super_admin_schools_list_html'),
    path('super-admin/schools/add.html', admin_views.school_add, name='super_admin_school_add'),
    path('super-admin/schools/edit.html', admin_views.school_edit, name='super_admin_school_edit'),
    path('super-admin/schools/details.html', admin_views.school_details, name='super_admin_school_details'),

    # Super Admin Calling Rules, Schedules, Validity & Recharges
    path('super-admin/calling-duration/', admin_views.calling_duration, name='super_admin_calling_duration'),
    path('super-admin/calling-duration/index.html', admin_views.calling_duration, name='super_admin_calling_duration_html'),
    path('super-admin/calling-schedules/', admin_views.calling_schedules, name='super_admin_calling_schedules'),
    path('super-admin/calling-schedules/index.html', admin_views.calling_schedules, name='super_admin_calling_schedules_html'),
    path('super-admin/validity/', admin_views.validity_overview, name='super_admin_validity'),
    path('super-admin/validity/overview.html', admin_views.validity_overview, name='super_admin_validity_overview_html'),
    path('super-admin/validity/rules.html', admin_views.validity_rules, name='super_admin_validity_rules_html'),
    path('super-admin/recharges/', admin_views.recharges_overview, name='super_admin_recharges'),
    path('super-admin/recharges/overview.html', admin_views.recharges_overview, name='super_admin_recharges_overview_html'),
    path('super-admin/recharges/create-plan.html', admin_views.recharge_create_plan, name='super_admin_recharge_create_plan'),
    path('super-admin/recharges/history.html', admin_views.recharge_history, name='super_admin_recharge_history'),

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
    path('franchise/students/add.html', franchise_views.student_add, name='franchise_student_add'),
    path('franchise/students/details.html', franchise_views.student_details, name='franchise_student_details'),
    path('franchise/students/edit.html', franchise_views.student_edit, name='franchise_student_edit'),
    path('franchise/classes/', franchise_views.classes_list, name='franchise_classes_list'),
    path('franchise/classes/index.html', franchise_views.classes_list, name='franchise_classes_list_html'),
    path('franchise/calling-duration/', franchise_views.calling_duration, name='franchise_calling_duration'),
    path('franchise/calling-duration/index.html', franchise_views.calling_duration, name='franchise_calling_duration_html'),
    path('franchise/calling-schedules/', franchise_views.calling_schedules, name='franchise_calling_schedules'),
    path('franchise/calling-schedules/index.html', franchise_views.calling_schedules, name='franchise_calling_schedules_html'),
    path('franchise/validity/', franchise_views.validity_overview, name='franchise_validity'),
    path('franchise/validity/index.html', franchise_views.validity_overview, name='franchise_validity_html'),
    path('franchise/recharges/', franchise_views.recharges_overview, name='franchise_recharges'),
    path('franchise/recharges/index.html', franchise_views.recharges_overview, name='franchise_recharges_html'),
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
    path('school-admin/calling-duration/', school_views.calling_duration, name='school_admin_calling_duration'),
    path('school-admin/calling-duration/index.html', school_views.calling_duration, name='school_admin_calling_duration_html'),
    path('school-admin/calling-schedules/', school_views.calling_schedules, name='school_admin_calling_schedules'),
    path('school-admin/calling-schedules/index.html', school_views.calling_schedules, name='school_admin_calling_schedules_html'),
    path('school-admin/validity/', school_views.validity_overview, name='school_admin_validity'),
    path('school-admin/validity/index.html', school_views.validity_overview, name='school_admin_validity_html'),
    path('school-admin/recharges/', school_views.recharges_overview, name='school_admin_recharges'),
    path('school-admin/recharges/overview.html', school_views.recharges_overview, name='school_admin_recharges_overview_html'),
    path('school-admin/recharges/student-recharge.html', school_views.student_recharge, name='school_admin_student_recharge_html'),
    path('school-admin/bulk-upload/', school_views.bulk_upload_students, name='school_admin_bulk_upload'),
    path('school-admin/bulk-upload/index.html', school_views.bulk_upload_students, name='school_admin_bulk_upload_html'),
    path('school-admin/bulk-upload/sample.csv', school_views.download_sample_csv, name='school_admin_bulk_upload_sample_csv'),
    path('school-admin/call-history/', school_views.call_history, name='school_admin_call_history'),
    path('school-admin/call-history/index.html', school_views.call_history, name='school_admin_call_history_html'),
    path('school-admin/hostel-wardens/', school_views.hostel_wardens_list, name='school_admin_hostel_wardens_list'),
    path('school-admin/hostel-wardens/list.html', school_views.hostel_wardens_list, name='school_admin_hostel_wardens_list_html'),
    path('school-admin/hostel-wardens/add.html', school_views.hostel_warden_add, name='school_admin_hostel_warden_add_html'),
    path('school-admin/hostel-wardens/edit.html', school_views.hostel_warden_edit, name='school_admin_hostel_warden_edit_html'),
    path('school-admin/hostel-wardens/details.html', school_views.hostel_warden_details, name='school_admin_hostel_warden_details_html'),
    path('school-admin/device-assignments/', school_views.device_assignments_list, name='school_admin_device_assignments_list'),
    path('school-admin/device-assignments/list.html', school_views.device_assignments_list, name='school_admin_device_assignments_list_html'),
    path('school-admin/device-assignments/assign.html', school_views.device_assign, name='school_admin_device_assign_html'),
    path('school-admin/student-reports/', school_views.student_reports, name='school_admin_student_reports'),
    path('school-admin/student-reports/index.html', school_views.student_reports, name='school_admin_student_reports_html'),
    path('school-admin/student-reports/export.csv', school_views.export_student_reports_csv, name='school_admin_student_reports_export_csv'),
    path('school-admin/class-reports/', school_views.class_reports, name='school_admin_class_reports'),
    path('school-admin/class-reports/index.html', school_views.class_reports, name='school_admin_class_reports_html'),
    path('school-admin/class-reports/export.csv', school_views.export_class_reports_csv, name='school_admin_class_reports_export_csv'),
    path('school-admin/settings/', school_views.school_settings, name='school_admin_settings'),
    path('school-admin/settings/index.html', school_views.school_settings, name='school_admin_settings_html'),
    re_path(r'^school-admin/(?P<path>.+?)/?$', school_views.render_school_page, name='school_admin_page'),

    # Student Kiosk Application & Telemetry Endpoints (Api_views.py)
    path('api/status/', Api_views.api_status, name='api_status'),
    path('api/whitelist/<str:student_id>/', Api_views.student_whitelist_check, name='api_whitelist_check'),
    path('api/kiosk/heartbeat/', Api_views.device_heartbeat, name='api_device_heartbeat'),

    # Fallback Template Router (for auth/, etc.)
    re_path(r'^(?!static/)(?P<path>.+?)/?$', views.render_template_page, name='render_page'),
]
