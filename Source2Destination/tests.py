from datetime import timedelta
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
from .models import School, Student, Guardian, HostelWarden, KioskDevice, DeviceAssignment, CallRecord, AcademicClass


class SchoolAdminFlowchartTests(TestCase):
    """
    Automated integration test suite verifying Section 3 (School Admin Panel)
    and Section 6 (Central Database) per source2destination_flowchart.pdf.
    """

    def setUp(self):
        # Retrieve or create school admin user (seeded by migration 0006)
        self.user, _ = User.objects.get_or_create(username='school', defaults={'email': 'school@s2d.com'})
        self.user.set_password('12345')
        self.user.save()

        self.school, _ = School.objects.get_or_create(
            code='SCH-1001',
            defaults={
                'name': 'Doon Valley Residential Academy',
                'city': 'Dehradun, Uttarakhand',
                'admin_name': 'Dr. Ramesh Chandra Sharma',
                'admin_email': 'principal@doonvalley.edu.in',
                'admin_phone': '+91 98101 23456'
            }
        )
        self.academic_class, _ = AcademicClass.objects.get_or_create(
            school=self.school,
            code='CLS-10',
            defaults={
                'name': 'Grade 10',
                'supervisor': 'Dr. Sharma'
            }
        )
        self.warden, _ = HostelWarden.objects.get_or_create(
            code='WRD-101',
            defaults={
                'school': self.school,
                'name': 'Major Rajeshwar Singh (Retd.)',
                'phone': '+91 98101 23481',
                'email': 'r.singh@doonvalley.edu.in',
                'hostel_block': 'Tagore Bhavan',
                'shift_timings': '16:00 – 00:00',
                'booths_monitored': 4,
                'status': 'On Duty'
            }
        )
        self.kiosk, _ = KioskDevice.objects.get_or_create(
            device_id='DEV-7701',
            defaults={
                'school': self.school,
                'name': 'Hostel Block A - Primary Booth',
                'serial_number': 'SN-7701-S2D',
                'hostel_block': 'Tagore Bhavan',
                'assigned_wing': 'Tagore Bhavan',
                'status': 'Online'
            }
        )
        self.client = Client()
        self.client.login(username='school', password='12345')

    def test_dashboard_and_telemetry(self):
        response = self.client.get('/school-admin/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Doon Valley Residential Academy')

    def test_call_history(self):
        response = self.client.get('/school-admin/call-history/')
        self.assertEqual(response.status_code, 200)

    def test_bulk_upload_and_sample(self):
        page_resp = self.client.get('/school-admin/bulk-upload/')
        self.assertEqual(page_resp.status_code, 200)
        sample_resp = self.client.get('/school-admin/bulk-upload/sample.csv')
        self.assertEqual(sample_resp.status_code, 200)
        self.assertIn(b'student_full_name', sample_resp.content)

    def test_hostel_warden_crud(self):
        list_resp = self.client.get('/school-admin/hostel-wardens/')
        self.assertEqual(list_resp.status_code, 200)

        add_resp = self.client.post('/school-admin/hostel-wardens/add.html', {
            'name': 'Inspector Vikram Rathore',
            'email': 'v.rathore@doonvalley.edu.in',
            'phone': '+91 98111 22334',
            'hostel_wing': 'Subhash Chandra Bose Block',
            'shift_hours': '16:00 – 00:00',
            'supervised_students': 60,
            'supervised_devices': 2,
            'status': 'On Duty'
        })
        self.assertIn(add_resp.status_code, [200, 302])
        self.assertTrue(HostelWarden.objects.filter(name='Inspector Vikram Rathore').exists())

    def test_device_assignments(self):
        list_resp = self.client.get('/school-admin/device-assignments/')
        self.assertEqual(list_resp.status_code, 200)
        assign_resp = self.client.get('/school-admin/device-assignments/assign.html')
        self.assertEqual(assign_resp.status_code, 200)

    def test_student_and_class_reports(self):
        st_rep = self.client.get('/school-admin/student-reports/')
        self.assertEqual(st_rep.status_code, 200)
        st_csv = self.client.get('/school-admin/student-reports/export.csv')
        self.assertEqual(st_csv.status_code, 200)
        self.assertIn(b'Student Code', st_csv.content)

        cl_rep = self.client.get('/school-admin/class-reports/')
        self.assertEqual(cl_rep.status_code, 200)
        cl_csv = self.client.get('/school-admin/class-reports/export.csv')
        self.assertEqual(cl_csv.status_code, 200)
        self.assertIn(b'Class Code', cl_csv.content)

    def test_school_settings_update(self):
        settings_page = self.client.get('/school-admin/settings/')
        self.assertEqual(settings_page.status_code, 200)

        update_resp = self.client.post('/school-admin/settings/index.html', {
            'school_name': 'Doon Valley Residential Academy',
            'admin_name': 'Dr. Ramesh Chandra Sharma',
            'admin_email': 'principal@doonvalley.edu.in',
            'admin_phone': '+91 98101 23456',
        })
        self.assertIn(update_resp.status_code, [200, 302])

    def test_calling_rules_and_recharges(self):
        for route in [
            '/school-admin/calling-schedules/',
            '/school-admin/calling-duration/',
            '/school-admin/validity/',
            '/school-admin/recharges/'
        ]:
            resp = self.client.get(route)
            self.assertEqual(resp.status_code, 200, f"Route {route} failed")

    def test_dashboard_live_kpis_charts_and_sidebar_active(self):
        student = Student.objects.create(
            code='STU-9001',
            calling_code='S2D-DOON-9001',
            school=self.school,
            name='Aarav Kulkarni',
            class_name='Grade 10',
            section='A',
            guardian_name='Suresh Kulkarni',
            guardian_relation='Father',
            primary_phone='+91 98101 55501',
            remaining_minutes=120,
            status='Active',
        )
        # 1 call today (Completed), 1 violation today, 1 historical call 3 days ago
        CallRecord.objects.create(
            call_id='CAL-TEST-TODAY-1',
            school=self.school,
            student=student,
            destination_number='+91 98101 55501',
            start_time=timezone.now(),
            duration_seconds=180,
            minutes_deducted=3,
            call_status='Completed',
        )
        CallRecord.objects.create(
            call_id='CAL-TEST-TODAY-2',
            school=self.school,
            student=student,
            destination_number='+91 98101 55501',
            start_time=timezone.now(),
            duration_seconds=0,
            minutes_deducted=0,
            call_status='Restricted Schedule',
        )
        CallRecord.objects.create(
            call_id='CAL-TEST-OLD-1',
            school=self.school,
            student=student,
            destination_number='+91 98101 55501',
            start_time=timezone.now() - timedelta(days=3),
            duration_seconds=300,
            minutes_deducted=5,
            call_status='Completed',
        )

        resp = self.client.get('/school-admin/dashboard.html')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['calls_today_count'], 2)
        self.assertEqual(resp.context['violations_today_count'], 1)
        self.assertEqual(resp.context['total_booths_count'], 1)
        self.assertEqual(resp.context['booths_online_percent'], 100.0)
        self.assertContains(resp, 'window.S2D_SCHOOL_CHARTS')
        self.assertContains(resp, 'Major Rajeshwar Singh (Retd.)')
        self.assertContains(resp, 'Aarav Kulkarni')
        # Active sidebar highlight on /school-admin/dashboard.html
        self.assertContains(resp, 'href="/school-admin/dashboard.html" class="sidebar-link active"')

    def test_device_assign_post_and_offline_rejection(self):
        # Assign online device succeeds
        ok_resp = self.client.post('/school-admin/device-assignments/assign.html', {
            'device_id': self.kiosk.device_id,
            'academic_class': 'Grade 10',
            'hostel_wing': 'Tagore Bhavan · Floor 2',
        })
        self.assertEqual(ok_resp.status_code, 302)
        self.assertTrue(DeviceAssignment.objects.filter(device=self.kiosk, hostel_wing='Tagore Bhavan · Floor 2').exists())

        # Offline device shows validation error
        offline_kiosk = KioskDevice.objects.create(
            device_id='DEV-7799',
            school=self.school,
            name='Offline Test Booth',
            hostel_block='Junior Wing',
            status='Offline',
        )
        err_resp = self.client.post('/school-admin/device-assignments/assign.html', {
            'device_id': offline_kiosk.device_id,
            'academic_class': 'Grade 10',
            'hostel_wing': 'Junior Wing',
        })
        self.assertEqual(err_resp.status_code, 200)
        self.assertContains(err_resp, 'currently Offline')

    def test_hostel_warden_edit_and_details(self):
        edit_resp = self.client.post(f'/school-admin/hostel-wardens/edit.html?id={self.warden.code}', {
            'name': 'Major Rajeshwar Singh (Retd.)',
            'email': 'rajeshwar@doonvalley.edu.in',
            'phone': '+91 98101 23499',
            'hostel_block': 'Tagore Bhavan',
            'shift_timings': '17:00 – 23:00',
            'status': 'On Duty',
        })
        self.assertEqual(edit_resp.status_code, 302)
        self.warden.refresh_from_db()
        self.assertEqual(self.warden.phone, '+91 98101 23499')

        det_resp = self.client.get(f'/school-admin/hostel-wardens/details.html?id={self.warden.code}')
        self.assertEqual(det_resp.status_code, 200)
        self.assertContains(det_resp, '+91 98101 23499')
        self.assertContains(det_resp, 'window.S2D_DEMO.devices')

    def test_reports_and_detail_live_json(self):
        student = Student.objects.create(
            code='STU-9002',
            calling_code='S2D-DOON-9002',
            school=self.school,
            name='Ananya Deshmukh',
            class_name='Grade 10',
            section='A',
            guardian_name='Prakash Deshmukh',
            guardian_relation='Father',
            primary_phone='+91 98101 66601',
            remaining_minutes=200,
            status='Active',
        )
        guardian = Guardian.objects.create(
            code='GRD-9002',
            school=self.school,
            student=student,
            name='Prakash Deshmukh',
            father_phone='+91 98101 66601',
            email='prakash@example.com',
        )

        st_rep = self.client.get('/school-admin/student-reports/')
        self.assertEqual(st_rep.status_code, 200)
        self.assertContains(st_rep, 'Ananya Deshmukh')
        self.assertEqual(st_rep.context['total_minutes'], 200)

        cl_rep = self.client.get('/school-admin/class-reports/')
        self.assertEqual(cl_rep.status_code, 200)
        self.assertContains(cl_rep, 'window.S2D_DEMO.classes')
        self.assertContains(cl_rep, 'window.S2D_SCHOOL_CHARTS')

        stu_det = self.client.get(f'/school-admin/students/details.html?id={student.code}')
        self.assertEqual(stu_det.status_code, 200)
        self.assertContains(stu_det, 'window.S2D_DEMO.callHistory')
        self.assertContains(stu_det, 'window.S2D_DEMO.recharges')

        grd_det = self.client.get(f'/school-admin/guardians/details.html?id={guardian.code}')
        self.assertEqual(grd_det.status_code, 200)
        self.assertContains(grd_det, 'window.S2D_DEMO.callHistory')

    def test_all_four_settings_tabs_persist(self):
        # Tab 1: Profile (school_name bug fixed)
        r1 = self.client.post('/school-admin/settings/index.html', {
            'settings_section': 'profile',
            'school_name': 'Doon Valley Boarding Academy',
            'admin_name': 'Dr. Ramesh Chandra Sharma',
            'admin_email': 'principal@doonvalley.edu.in',
            'admin_phone': '+91 98101 23456',
        })
        self.assertEqual(r1.status_code, 200)
        self.assertContains(r1, 'saved successfully')
        self.school.refresh_from_db()
        self.assertEqual(self.school.name, 'Doon Valley Boarding Academy')

        # Tab 2: Caller ID Policies
        r2 = self.client.post('/school-admin/settings/index.html', {
            'settings_section': 'callerid',
            'display_school_caller_id': 'on',
            'show_guardian_whitelist_numbers': 'on',
        })
        self.assertEqual(r2.status_code, 200)
        self.school.refresh_from_db()
        self.assertTrue(self.school.display_school_caller_id)
        self.assertTrue(self.school.show_guardian_whitelist_numbers)
        self.assertFalse(self.school.emergency_override_caller_id)

        # Tab 3: Emergency Override Contacts
        r3 = self.client.post('/school-admin/settings/index.html', {
            'settings_section': 'emergency',
            'primary_emergency_phone': '+91 99999 11111',
            'secondary_emergency_phone': '+91 99999 22222',
            'warden_escalation_phone': '+91 99999 33333',
        })
        self.assertEqual(r3.status_code, 200)
        self.school.refresh_from_db()
        self.assertEqual(self.school.primary_emergency_phone, '+91 99999 11111')
        self.assertEqual(self.school.warden_escalation_phone, '+91 99999 33333')

        # Tab 4: Notification Channels
        r4 = self.client.post('/school-admin/settings/index.html', {
            'settings_section': 'notify',
            'notify_sms_guardians': 'on',
            'notify_email_recharges': 'on',
        })
        self.assertEqual(r4.status_code, 200)
        self.school.refresh_from_db()
        self.assertTrue(self.school.notify_sms_guardians)
        self.assertTrue(self.school.notify_email_recharges)
        self.assertFalse(self.school.notify_push_validity)
