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
    re_path(r'^franchise/(?P<path>.+?)/?$', franchise_views.render_franchise_page, name='franchise_page'),

    # School Admin Environment
    path('school-admin/', school_views.dashboard, name='school_admin_dashboard'),
    path('school-admin/dashboard.html', school_views.dashboard, name='school_admin_dashboard_html'),
    path('school-admin/students/', school_views.students_list, name='school_admin_students_list'),
    path('school-admin/students/list.html', school_views.students_list, name='school_admin_students_list_html'),
    path('school-admin/students/add.html', school_views.student_add, name='school_admin_student_add'),
    path('school-admin/students/details.html', school_views.student_details, name='school_admin_student_details'),
    path('school-admin/students/edit.html', school_views.student_edit, name='school_admin_student_edit'),
    re_path(r'^school-admin/(?P<path>.+?)/?$', school_views.render_school_page, name='school_admin_page'),

    # High-Performance REST API Endpoints (Api_views.py)
    # Schools APIs
    path('api/v1/super-admin/schools/', Api_views.schools_collection_api, name='api_super_admin_schools'),
    path('api/v1/super-admin/schools/bulk-status/', Api_views.school_bulk_status_api, name='api_super_admin_schools_bulk'),
    path('api/v1/super-admin/schools/<str:school_id>/', Api_views.school_item_api, name='api_super_admin_school_item'),
    path('api/v1/franchise/schools/', Api_views.franchise_schools_api, name='api_franchise_schools'),

    # Students APIs
    path('api/v1/students/', Api_views.students_collection_api, name='api_students_collection'),
    path('api/v1/students/bulk-status/', Api_views.student_bulk_status_api, name='api_students_bulk_status'),
    path('api/v1/students/<str:student_id>/', Api_views.student_item_api, name='api_student_item'),
    path('api/v1/franchise/students/', Api_views.franchise_students_api, name='api_franchise_students'),
    path('api/v1/school-admin/students/', Api_views.school_admin_students_api, name='api_school_admin_students'),

    # Telemetry and Health
    path('api/status/', Api_views.api_status, name='api_status'),
    path('api/whitelist/<str:student_id>/', Api_views.student_whitelist_check, name='api_whitelist_check'),
    path('api/kiosk/heartbeat/', Api_views.device_heartbeat, name='api_device_heartbeat'),

    # Fallback Template Router (for auth/, etc.)
    re_path(r'^(?!static/)(?P<path>.+?)/?$', views.render_template_page, name='render_page'),
]
