from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import School, Student, HostelWarden, KioskDevice, CallRecord, AcademicClass


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
