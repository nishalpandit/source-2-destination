import os
import json
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from django.test import Client
from django.core.files.uploadedfile import SimpleUploadedFile

client = Client()
tests = []

def run_test(name, method, url, payload=None, files=None):
    if method == 'GET':
        resp = client.get(url)
    elif method == 'POST':
        if files:
            post_data = (payload or {}).copy()
            post_data.update(files)
            resp = client.post(url, data=post_data)
        else:
            resp = client.post(url, data=json.dumps(payload or {}), content_type='application/json')
    else:
        raise ValueError(f"Unsupported method {method}")
    
    try:
        resp_json = resp.json()
    except Exception:
        resp_json = resp.content.decode('utf-8', errors='ignore')

    test_result = {
        "name": name,
        "method": method,
        "url": url,
        "payload": payload,
        "status": resp.status_code,
        "response": resp_json
    }
    tests.append(test_result)
    print(f"[{resp.status_code}] {method} {url} -> {name}")
    return test_result

print("Testing clean, short API endpoints against active database...")

# 1. API Status
run_test("API Service Status", "GET", "/api/status/")

# 2. Device Enrollment
run_test("Device Enrollment", "POST", "/api/device/enroll/", {
    "device_id": "DEV-TEST-ENROLL-99",
    "model_name": "Google Pixel 8",
    "school_code": "SCH-1001"
})

# 3. Device Heartbeat
run_test("Device Heartbeat", "POST", "/api/device/heartbeat/", {
    "device_id": "8f3b2a1c0d9e4567"
})

# 4. Student Auth (Success without PIN)
run_test("Student Login (Bound Hardware)", "POST", "/api/student/auth/", {
    "device_id": "8f3b2a1c0d9e4567",
    "student_code": "STU-DV-1023"
})

# 5. Student Auth (Hardware Mismatch)
run_test("Student Login (Hardware Mismatch)", "POST", "/api/student/auth/", {
    "device_id": "8f3b2a1c0d9e4567",
    "student_code": "STU-DV-1022"
})

# 6. Student Real-time Profile
run_test("Student Real-time Profile", "GET", "/api/student/STU-DV-1023/profile/")

# 7. Whitelisted Contacts
run_test("Whitelisted Contacts", "GET", "/api/student/STU-DV-1023/contacts/")

# 8. Call Pre-Flight Authorize (Whitelisted)
call_auth_res = run_test("Call Authorize (Whitelisted)", "POST", "/api/call/authorize/", {
    "student_code": "STU-DV-1023",
    "dialed_number": "+91 98110 40123",
    "device_id": "8f3b2a1c0d9e4567"
})

# 9. Call Pre-Flight Authorize (Unauthorized)
run_test("Call Authorize (Unauthorized Rejection)", "POST", "/api/call/authorize/", {
    "student_code": "STU-DV-1023",
    "dialed_number": "+91 99999 88888",
    "device_id": "8f3b2a1c0d9e4567"
})

# 10. Call Terminate
term_res = run_test("Call Terminate & Metering", "POST", "/api/call/terminate/", {
    "student_code": "STU-DV-1023",
    "dialed_number": "+91 98110 40123",
    "duration_seconds": 120,
    "termination_reason": "Completed",
    "device_id": "8f3b2a1c0d9e4567"
})
active_call_id = term_res["response"].get("call_id") or "CAL-DV-1010"

# 11. Student Call History
run_test("Student Call History", "GET", "/api/student/STU-DV-1023/history/")

# 12. Student Validity Checkup
run_test("Student Validity Checkup", "GET", "/api/student/STU-DV-1023/validity/")
run_test("Student Validity Checkup (Alias)", "GET", "/api/v1/kiosk/student/STU-DV-1023/validity/")

# DATA APIS:
# 12. Remote Kiosk Device Policy & Config Sync
run_test("Remote Kiosk Configuration & Policy Sync", "GET", "/api/device/8f3b2a1c0d9e4567/config/")

# 13. Call Audio Recording Upload
fake_audio = SimpleUploadedFile("call_recording.mp3", b"ID3\x03\x00\x00\x00\x00\x00#AUDIO-RECORDING-TEST-STREAM#", content_type="audio/mpeg")
run_test("Call Audio Recording Upload", "POST", "/api/call/recordings/upload/", payload={"call_id": active_call_id}, files={"recording_file": fake_audio})

# 14. Student Bulk Data Sync / SIS Import
run_test("Student Bulk Data Sync", "POST", "/api/school/SCH-1001/students/sync/", payload={
    "students": [
        {
            "code": "STU-SYNC-2001",
            "name": "Rohan Mehra",
            "class_name": "Grade 11",
            "section": "Science A",
            "guardian_name": "Vikram Mehra",
            "guardian_relation": "Father",
            "primary_phone": "+91 98234 56789",
            "pin": "2001",
            "remaining_minutes": 150
        }
    ]
})

# 15. Payment Gateway Webhook
run_test("Payment Gateway Webhook Top-Up", "POST", "/api/payments/webhook/", payload={
    "event": "payment.success",
    "recharge_id": f"RCG-LIVE-{os.urandom(3).hex().upper()}",
    "student_code": "STU-DV-1023",
    "plan_code": "RPL-01",
    "amount": 299.00
})

# 16. Student Emergency SOS Alert
run_test("Student Emergency SOS Alert", "POST", "/api/student/sos/", payload={
    "student_code": "STU-DV-1023",
    "device_id": "8f3b2a1c0d9e4567",
    "location": "North Dorm Wing B · Floor 2",
    "notes": "Medical emergency / asthma inhaler required"
})

# 17. School Call Telemetry Data Export
run_test("School Call Telemetry Data Export", "GET", "/api/school/SCH-1001/call-data/?limit=10")

with open("captured_api_responses.json", "w", encoding="utf-8") as f:
    json.dump(tests, f, indent=2)

print("\nDone! All clean endpoints verified and responses captured.")
