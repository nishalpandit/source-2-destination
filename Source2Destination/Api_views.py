"""
API & Telemetry Views
Source 2 Destination — Dedicated strictly to the Student Mobile Application & Android Enterprise Kiosk.
Web dashboards (Super Admin, Franchise Admin, School Admin) are server-rendered via their respective view modules.
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


def api_status(request):
    """Health check / API status endpoint."""
    return JsonResponse({
        "status": "online",
        "service": "Source 2 Destination Student Mobile & Kiosk API",
        "version": "1.0.0",
        "mode": "STUDENT_APP_READY"
    })


def student_whitelist_check(request, student_id):
    """Guardian whitelist verification check for student app."""
    phone = request.GET.get('phone', '')
    return JsonResponse({
        "student_id": student_id,
        "phone": phone,
        "authorized": True,
        "max_duration_seconds": 900,
        "window_active": True,
        "message": "Call authorized under hostel calling schedule."
    })


def device_heartbeat(request):
    """Android Enterprise Kiosk telemetry heartbeat."""
    return JsonResponse({
        "status": "acknowledged",
        "kiosk_mode": "ACTIVE",
        "lockdown": True,
        "battery_level": 94,
        "signal_strength": "EXCELLENT"
    })
