"""
API & Telemetry Views
Source 2 Destination — REST API & Device Telemetry Endpoints
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

def api_status(request):
    """Health check / API status endpoint."""
    return JsonResponse({
        "status": "online",
        "service": "Source 2 Destination Calling Governance API",
        "version": "1.0.0",
        "mode": "DRF_READY"
    })

def student_whitelist_check(request, student_id):
    """
    Simulated guardian whitelist verification endpoint.
    Verifies that target dial number is whitelisted for the given student.
    """
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
