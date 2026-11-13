"""
Application URL Configuration
Routes split cleanly across Super Admin, Franchise, School Admin, and API modules.
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

    # Super Admin Environment
    path('super-admin/', admin_views.dashboard, name='super_admin_dashboard'),
    path('super-admin/dashboard.html', admin_views.dashboard, name='super_admin_dashboard_html'),
    re_path(r'^super-admin/(?P<path>.+?)/?$', admin_views.render_admin_page, name='super_admin_page'),

    # Franchise Partner Environment
    path('franchise/', franchise_views.dashboard, name='franchise_dashboard'),
    path('franchise/dashboard.html', franchise_views.dashboard, name='franchise_dashboard_html'),
    re_path(r'^franchise/(?P<path>.+?)/?$', franchise_views.render_franchise_page, name='franchise_page'),

    # School Admin Environment
    path('school-admin/', school_views.dashboard, name='school_admin_dashboard'),
    path('school-admin/dashboard.html', school_views.dashboard, name='school_admin_dashboard_html'),
    re_path(r'^school-admin/(?P<path>.+?)/?$', school_views.render_school_page, name='school_admin_page'),

    # API Endpoints
    path('api/status/', Api_views.api_status, name='api_status'),
    path('api/whitelist/<str:student_id>/', Api_views.student_whitelist_check, name='api_whitelist_check'),
    path('api/kiosk/heartbeat/', Api_views.device_heartbeat, name='api_device_heartbeat'),

    # Fallback Template Router (for auth/, etc.)
    re_path(r'^(?!static/)(?P<path>.+?)/?$', views.render_template_page, name='render_page'),
]
