from datetime import timedelta
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
from .models import (
    School, Student, Guardian, HostelWarden, KioskDevice, DeviceAssignment,
    CallRecord, AcademicClass, ClassSection, Franchise, StudentRecharge, RechargePlan
)


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
        self.assertNotContains(resp, 'Hostel Calling Booths &amp; Duty Roster')
        self.assertNotContains(resp, 'Enrolled Students &amp; Account Status')
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

        codes_resp = self.client.get('/school-admin/student-codes/')
        self.assertEqual(codes_resp.status_code, 200)
        self.assertContains(codes_resp, 'Ananya Deshmukh')
        self.assertContains(codes_resp, 'S2D-DOON-9002')
        self.assertNotContains(codes_resp, 'No codes issued yet.')

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

    def test_student_add_and_edit_fields(self):
        # Test enrolling student with validity date and hostel booth
        enroll_resp = self.client.post('/school-admin/students/add.html', {
            'name': 'Devansh Singhal',
            'gender': 'Male',
            'className': 'Grade 10',
            'section': 'Section A',
            'roll_number': '1088',
            'hostelWing': 'Tagore Bhavan · Rm 102',
            'guardian_name': 'Alok Singhal (Father)',
            'primary_phone': '+91 98111 22334',
            'secondary_phone': '+91 98111 22335',
            'validity_expiry': '2027-08-31',
            'device_id': 'DEV-7701',
            'status': 'Active'
        })
        self.assertEqual(enroll_resp.status_code, 302)

        stu = Student.objects.filter(name='Devansh Singhal').first()
        self.assertIsNotNone(stu)
        self.assertEqual(str(stu.validity_expiry), '2027-08-31')
        self.assertEqual(stu.roll_number, '1088')
        self.assertEqual(stu.gender, 'Male')

        # Check guardian was created with both numbers
        guardian = stu.guardian_contacts.first()
        self.assertIsNotNone(guardian)
        self.assertEqual(guardian.father_phone, '+91 98111 22334')
        self.assertEqual(guardian.mother_phone, '+91 98111 22335')

        # Check device mapping created
        assignment = DeviceAssignment.objects.filter(school=self.school, device=self.kiosk).first()
        self.assertIsNotNone(assignment)

        # Test editing student
        edit_resp = self.client.post(f'/school-admin/students/edit.html?id={stu.code}', {
            'name': 'Devansh Singhal Updated',
            'gender': 'Male',
            'className': 'Grade 10',
            'section': 'Section B',
            'roll_number': '1099',
            'hostelWing': 'Tagore Bhavan · Rm 204',
            'guardianName': 'Alok Singhal',
            'primaryPhone': '+91 98111 99999',
            'secondaryPhone': '+91 98111 88888',
            'validityExpiry': '2028-03-31',
            'remainingMinutes': '180',
            'dailyLimitMin': '20',
            'status': 'Active'
        })
        self.assertEqual(edit_resp.status_code, 302)

        stu.refresh_from_db()
        self.assertEqual(stu.name, 'Devansh Singhal Updated')
        self.assertEqual(stu.roll_number, '1099')
        self.assertEqual(str(stu.validity_expiry), '2028-03-31')
        self.assertEqual(stu.primary_phone, '+91 98111 99999')
        self.assertEqual(stu.remaining_minutes, 180)

        # Verify linked guardian was synchronized
        guardian.refresh_from_db()
        self.assertEqual(guardian.father_phone, '+91 98111 99999')
        self.assertEqual(guardian.name, 'Alok Singhal')

    def test_super_admin_school_edit_comprehensive(self):
        # Create and log in as super admin
        admin_user, _ = User.objects.get_or_create(username='admin', defaults={'email': 'admin@s2d.com', 'is_staff': True, 'is_superuser': True})
        admin_user.set_password('12345')
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()

        admin_client = Client()
        admin_client.login(username='admin', password='12345')

        edit_resp = admin_client.post(f'/super-admin/schools/edit.html?id={self.school.code}', {
            'name': 'Doon Valley International School',
            'campus_type': 'Co-ed Residential Boarding',
            'affiliation_board': 'CBSE',
            'website': 'https://doonvalley.edu.in',
            'city': 'Dehradun',
            'state': 'Uttarakhand',
            'postal_code': '248001',
            'country': 'India',
            'hostel_blocks_count': '6',
            'timezone': 'Asia/Kolkata',
            'address': 'Chakrata Road, Dehradun',
            'admin_name': 'Dr. R.C. Sharma',
            'admin_email': 'director@doonvalley.edu.in',
            'admin_phone': '+91 98101 99999',
            'subscription_plan': 'Enterprise Boarding Annual',
            'billing_cycle': 'Annually',
            'student_seats': '850',
            'daily_duration_cap': '20',
            'calling_window_start': '16:30',
            'calling_window_end': '20:00',
            'allowed_calling_days': 'All 7 Days',
            'emergency_calling_allowed': 'on',
            'status': 'Active'
        })
        self.assertEqual(edit_resp.status_code, 302)

        self.school.refresh_from_db()
        self.assertEqual(self.school.name, 'Doon Valley International School')
        self.assertEqual(self.school.city, 'Dehradun')
        self.assertEqual(self.school.state, 'Uttarakhand')
        self.assertEqual(self.school.hostel_blocks_count, 6)
        self.assertEqual(self.school.timezone, 'Asia/Kolkata')
        self.assertEqual(self.school.admin_phone, '+91 98101 99999')
        self.assertEqual(self.school.daily_duration_cap, 20)
        self.assertTrue(self.school.emergency_calling_allowed)

    def test_student_pin_dob_wallet_crud(self):
        # 1. Enroll new student with DOB, PIN, and initial prepaid wallet balance
        resp = self.client.post('/school-admin/students/add.html', {
            'name': 'Vihaan Kapoor',
            'gender': 'Male',
            'date_of_birth': '2010-06-18',
            'pin': '7788',
            'wallet_balance': '350.00',
            'class_grade': 'Grade 10',
            'section': 'Section A',
            'roll_number': '1042',
            'hostel_wing': 'Tagore Wing · Rm 302',
            'guardian_name': 'Rajesh Kapoor',
            'relation': 'Father',
            'primary_phone': '+91 98222 11111',
            'secondary_phone': '+91 98222 22222',
            'validity_expiry': '2028-06-30',
            'allocated_minutes': 200,
            'daily_limit_minutes': 25,
            'status': 'Active'
        })
        self.assertIn(resp.status_code, [200, 302])

        stu = Student.objects.filter(school=self.school, name='Vihaan Kapoor').first()
        self.assertIsNotNone(stu)
        self.assertEqual(str(stu.date_of_birth), '2010-06-18')
        self.assertEqual(stu.pin, '7788')
        self.assertEqual(float(stu.wallet_balance), 350.00)
        self.assertEqual(stu.roll_number, '1042')

        # 2. Edit student details including updated PIN, DOB, and wallet balance
        edit_resp = self.client.post(f'/school-admin/students/edit.html?id={stu.code}', {
            'name': 'Vihaan Kapoor',
            'gender': 'Male',
            'date_of_birth': '2010-06-18',
            'pin': '9900',
            'wallet_balance': '500.00',
            'className': 'Grade 10',
            'section': 'Section A',
            'rollNumber': '1042',
            'hostelWing': 'Tagore Wing · Rm 302',
            'guardianName': 'Rajesh Kapoor',
            'primaryPhone': '+91 98222 11111',
            'secondaryPhone': '+91 98222 33333',
            'validityExpiry': '2028-12-31',
            'remainingMinutes': '250',
            'dailyLimitMin': '30',
            'status': 'Active'
        })
        self.assertEqual(edit_resp.status_code, 302)

        stu.refresh_from_db()
        self.assertEqual(stu.pin, '9900')
        self.assertEqual(float(stu.wallet_balance), 500.00)
        self.assertEqual(stu.remaining_minutes, 250)

    def test_classes_and_sections_edit_and_archive(self):
        # 1. Edit existing academic class
        edit_cls_resp = self.client.post('/school-admin/classes/', {
            'action': 'edit',
            'class_code': self.academic_class.code,
            'className': 'Grade 10 Advanced STEM',
            'supervisor': 'Prof. Ananya Sen',
            'defaultDailyMinutes': '25',
            'schedule_group': 'Extended Boarding Window',
            'status': 'Active'
        })
        self.assertEqual(edit_cls_resp.status_code, 302)
        self.academic_class.refresh_from_db()
        self.assertEqual(self.academic_class.name, 'Grade 10 Advanced STEM')
        self.assertEqual(self.academic_class.supervisor, 'Prof. Ananya Sen')
        self.assertEqual(self.academic_class.default_daily_minutes, 25)

        # 2. Archive class
        del_cls_resp = self.client.post('/school-admin/classes/', {
            'action': 'archive',
            'class_code': self.academic_class.code
        })
        self.assertEqual(del_cls_resp.status_code, 302)
        self.academic_class.refresh_from_db()
        self.assertEqual(self.academic_class.status, 'Archived')

        # 3. Create, Edit, and Archive Section
        section = ClassSection.objects.create(
            school=self.school,
            academic_class=self.academic_class,
            code='SEC-10A',
            name='Section 10-A',
            room_wing='East Wing - Rm 101',
            advisor='Dr. Sen',
            status='Active'
        )

        edit_sec_resp = self.client.post('/school-admin/classes/sections.html', {
            'action': 'edit',
            'section_code': section.code,
            'sectionName': 'Section 10-A Prime',
            'roomWing': 'East Wing - Rm 105',
            'advisor': 'Dr. Vikram Sen',
            'status': 'Active'
        })
        self.assertEqual(edit_sec_resp.status_code, 302)
        section.refresh_from_db()
        self.assertEqual(section.name, 'Section 10-A Prime')
        self.assertEqual(section.room_wing, 'East Wing - Rm 105')

        del_sec_resp = self.client.post('/school-admin/classes/sections.html', {
            'action': 'archive',
            'section_code': section.code
        })
        self.assertEqual(del_sec_resp.status_code, 302)
        section.refresh_from_db()
        self.assertEqual(section.status, 'Archived')

    def test_super_admin_school_caller_id_and_emergency_overrides(self):
        admin_user, _ = User.objects.get_or_create(username='admin', defaults={'email': 'admin@s2d.com', 'is_staff': True, 'is_superuser': True})
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()

        admin_client = Client()
        admin_client.login(username='admin', password='12345')

        # Test updating emergency overrides and caller ID on school
        edit_resp = admin_client.post(f'/super-admin/schools/edit.html?id={self.school.code}', {
            'name': 'Doon Valley International School',
            'city': 'Dehradun',
            'admin_name': 'Dr. R.C. Sharma',
            'admin_email': 'director@doonvalley.edu.in',
            'admin_phone': '+91 98101 99999',
            'primary_emergency_phone': '+91 98101 00112',
            'secondary_emergency_phone': '+91 98101 00113',
            'warden_escalation_phone': '+91 98101 00114',
            'display_school_caller_id': 'on',
            'show_guardian_whitelist_numbers': 'on',
            'notify_sms_guardians': 'on',
            'status': 'Active'
        })
        self.assertEqual(edit_resp.status_code, 302)

        self.school.refresh_from_db()
        self.assertEqual(self.school.primary_emergency_phone, '+91 98101 00112')
        self.assertEqual(self.school.secondary_emergency_phone, '+91 98101 00113')
        self.assertEqual(self.school.warden_escalation_phone, '+91 98101 00114')
        self.assertTrue(self.school.display_school_caller_id)
        self.assertTrue(self.school.show_guardian_whitelist_numbers)
        self.assertTrue(self.school.notify_sms_guardians)


class FranchisePortalTests(TestCase):
    """
    Automated integration test suite verifying Franchise Partner Portal
    functionality, dynamic database binding, commissions ledger,
    transactions, regional call telemetry, bulk upload, reports, and settings.
    """

    def setUp(self):
        self.user, _ = User.objects.get_or_create(username='franchise', defaults={'email': 'partner@northedunet.in'})
        self.user.set_password('12345')
        self.user.save()

        self.franchise, _ = Franchise.objects.get_or_create(
            code='FRN-101',
            defaults={
                'name': 'North India EduNet Partners',
                'partner_contact': 'Vikramaditya Singhania',
                'email': 'v.singhania@northedunet.in',
                'phone': '+91 98101 44550',
                'commission_rate': 18.00,
                'territory': 'Northern Region',
                'status': 'Active'
            }
        )

        self.school, _ = School.objects.get_or_create(
            code='SCH-1001',
            defaults={
                'name': 'Doon Valley Residential Academy',
                'city': 'Dehradun',
                'state': 'Uttarakhand',
                'franchise': self.franchise,
                'admin_name': 'Dr. Sharma',
                'admin_email': 'admin@doonvalley.edu.in',
                'admin_phone': '+91 98101 23456',
                'student_seats': 400,
                'enrolled_students': 350,
                'active_students': 340,
                'daily_duration_cap': 15,
                'status': 'Active'
            }
        )
        if self.school.franchise != self.franchise:
            self.school.franchise = self.franchise
            self.school.save(update_fields=['franchise'])

        self.student, _ = Student.objects.get_or_create(
            code='STU-4001',
            defaults={
                'calling_code': 'S2D-SCH-8801',
                'name': 'Aarav Sharma',
                'gender': 'Male',
                'school': self.school,
                'class_name': 'Grade 10',
                'section': 'Section A',
                'guardian_name': 'Rajesh Sharma',
                'primary_phone': '+919810123456',
                'pin': '1234',
                'wallet_balance': 50.00,
                'remaining_minutes': 120,
                'daily_limit_min': 15,
                'status': 'Active'
            }
        )

        self.recharge = StudentRecharge.objects.create(
            recharge_id='RCG-TEST-001',
            student=self.student,
            school=self.school,
            plan_name_cache='Term Calling Pack',
            amount=1000.00,
            minutes_added=150,
            validity_days_added=30,
            payment_mode='Campus Bursar Desk',
            voucher_ref='VCH-99881',
            status='Successful'
        )

        self.call = CallRecord.objects.create(
            call_id='CAL-TEST-001',
            school=self.school,
            student=self.student,
            destination_number='+919810123456',
            call_type='Father',
            duration_seconds=180,
            minutes_deducted=3,
            call_status='Completed'
        )

        self.client = Client()
        self.client.login(username='franchise', password='12345')

    def test_franchise_dashboard(self):
        resp = self.client.get('/franchise/dashboard.html')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'North India EduNet Partners')
        self.assertContains(resp, 'window.S2D_FRANCHISE_CHARTS')

    def test_franchise_commissions_ledger(self):
        resp = self.client.get('/franchise/commissions/index.html')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Revenue &amp; Commission Management')
        self.assertContains(resp, 'window.S2D_DEMO.commissions')
        self.assertContains(resp, 'window.S2D_FRANCHISE_CHARTS')

    def test_franchise_transactions_history(self):
        resp = self.client.get('/franchise/transactions/index.html')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Franchise Payment &amp; Transaction History')
        self.assertContains(resp, 'window.S2D_DEMO.transactions')

    def test_franchise_call_history(self):
        resp = self.client.get('/franchise/call-history/index.html')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Assigned-School Call History')
        self.assertContains(resp, 'window.S2D_DEMO.callHistory')

    def test_franchise_bulk_upload_flow(self):
        page_resp = self.client.get('/franchise/bulk-upload/')
        self.assertEqual(page_resp.status_code, 200)

        sample_resp = self.client.get('/franchise/bulk-upload/sample.csv')
        self.assertEqual(sample_resp.status_code, 200)
        self.assertIn(b'student_full_name', sample_resp.content)

        # Upload a test CSV
        from django.core.files.uploadedfile import SimpleUploadedFile
        csv_content = (
            "student_full_name,class_grade,section,father_authorized_phone,guardian_name,gender,pin,school_code\n"
            "Ananya Sen,Grade 10,Section B,+919811122334,Priya Sen,Female,4321,SCH-1001\n"
        ).encode('utf-8')
        upload_file = SimpleUploadedFile("students.csv", csv_content, content_type="text/csv")

        post_resp = self.client.post('/franchise/bulk-upload/index.html', {
            'school_id': self.school.code,
            'spreadsheet': upload_file
        })
        self.assertEqual(post_resp.status_code, 200)
        self.assertTrue(Student.objects.filter(name='Ananya Sen', school=self.school).exists())

    def test_franchise_reports_and_export(self):
        resp = self.client.get('/franchise/reports/index.html')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'window.S2D_DEMO.schools')

        csv_resp = self.client.get('/franchise/reports/export.csv')
        self.assertEqual(csv_resp.status_code, 200)
        self.assertIn(b'School Code', csv_resp.content)
        self.assertIn(b'Doon Valley Residential Academy', csv_resp.content)

    def test_franchise_settings_update(self):
        get_resp = self.client.get('/franchise/settings/index.html')
        self.assertEqual(get_resp.status_code, 200)

        post_resp = self.client.post('/franchise/settings/index.html', {
            'name': 'North India EduNet Holdings',
            'partner_contact': 'V. Singhania',
            'email': 'director@northedunet.in',
            'phone': '+91 98101 99999',
            'territory': 'Northern & North-Eastern Region'
        })
        self.assertEqual(post_resp.status_code, 200)

        self.franchise.refresh_from_db()
        self.assertEqual(self.franchise.name, 'North India EduNet Holdings')
        self.assertEqual(self.franchise.partner_contact, 'V. Singhania')
        self.assertEqual(self.franchise.email, 'director@northedunet.in')

    def test_franchise_student_pin_dob_wallet_crud(self):
        # Create student with PIN and DOB
        add_resp = self.client.post('/franchise/students/add.html', {
            'school': self.school.code,
            'name': 'Kavya Mehra',
            'className': 'Grade 11',
            'section': 'Section B',
            'guardianName': 'Suresh Mehra',
            'primaryPhone': '+919876543210',
            'pin': '7788',
            'date_of_birth': '2008-06-15',
            'wallet_balance': '150.00'
        })
        self.assertEqual(add_resp.status_code, 302)

        stu = Student.objects.filter(name='Kavya Mehra').first()
        self.assertIsNotNone(stu)
        self.assertEqual(stu.pin, '7788')
        self.assertEqual(str(stu.date_of_birth), '2008-06-15')
        self.assertEqual(float(stu.wallet_balance), 150.00)

        # Edit student
        edit_resp = self.client.post(f'/franchise/students/edit.html?id={stu.code}', {
            'name': 'Kavya Mehra (Honors)',
            'className': 'Grade 11',
            'section': 'Section A',
            'primaryPhone': '+919876543210',
            'pin': '9900',
            'date_of_birth': '2008-06-16',
            'wallet_balance': '200.00',
            'status': 'Active'
        })
        self.assertEqual(edit_resp.status_code, 302)

        stu.refresh_from_db()
        self.assertEqual(stu.name, 'Kavya Mehra (Honors)')
        self.assertEqual(stu.pin, '9900')
        self.assertEqual(str(stu.date_of_birth), '2008-06-16')
        self.assertEqual(float(stu.wallet_balance), 200.00)

    def test_franchise_school_emergency_settings(self):
        edit_resp = self.client.post(f'/franchise/schools/edit.html?id={self.school.code}', {
            'name': 'Doon Valley Residential Academy (Main Campus)',
            'city': 'Dehradun',
            'state': 'Uttarakhand',
            'adminName': 'Dr. Sharma',
            'adminEmail': 'admin@doonvalley.edu.in',
            'phone': '+91 98101 23456',
            'daily_duration_cap': 25,
            'kiosk_group_tag': 'AE-BOOTH-DORM-NORTH',
            'emergency_calling_allowed': 'on'
        })
        self.assertEqual(edit_resp.status_code, 302)

        self.school.refresh_from_db()
        self.assertEqual(self.school.name, 'Doon Valley Residential Academy (Main Campus)')
        self.assertEqual(self.school.daily_duration_cap, 25)
        self.assertEqual(self.school.kiosk_group_tag, 'AE-BOOTH-DORM-NORTH')
        self.assertTrue(self.school.emergency_calling_allowed)


class CallingEngineSessionTests(TestCase):
    """
    Division I automated verification:
    Validates CallSessionManager, CallAuthorizationEngine, and Core Enterprise Models.
    """
    def setUp(self):
        self.school = School.objects.create(
            code='SCH-TEST-01',
            name='Test Residential Academy',
            city='Dehradun',
            admin_name='Admin Test',
            admin_email='adm@test.edu',
            daily_duration_cap=20
        )
        self.student = Student.objects.create(
            school=self.school,
            code='STU-TEST-99',
            calling_code='8899',
            name='Aarav Sharma',
            class_name='Grade 10',
            section='A',
            guardian_name='Vikram Sharma',
            primary_phone='+919876543210',
            remaining_minutes=45,
            validity_expiry=timezone.now().date() + timedelta(days=30),
            status='Active',
            code_status='Active'
        )
        from datetime import time
        from .models import CallingScheduleRule
        CallingScheduleRule.objects.create(
            school=self.school,
            name='All Day Allowed Test Window',
            days_of_week='ALL',
            start_time=time(0, 0),
            end_time=time(23, 59, 59),
            policy_type='allowed',
            is_active=True
        )

    def test_call_session_initiate_and_terminate(self):
        from .calling_services import CallSessionManager

        # 1. Initiate session with whitelisted number
        init_res = CallSessionManager.initiate_session(self.student.calling_code, '+919876543210', 'DEV-BOOTH-1')
        self.assertTrue(init_res['authorized'])
        self.assertIsNotNone(init_res['session_token'])
        self.assertEqual(init_res['student_code'], 'STU-TEST-99')
        self.assertEqual(init_res['recipient_name'], 'Vikram Sharma')

        # 2. Terminate session after 125 seconds (ceil -> 3 minutes)
        term_res = CallSessionManager.terminate_session(
            self.student.calling_code,
            '+919876543210',
            duration_seconds=125,
            termination_reason='Completed',
            device_id='DEV-BOOTH-1'
        )
        self.assertTrue(term_res['success'])
        self.assertEqual(term_res['minutes_deducted'], 3)
        self.assertEqual(term_res['previous_balance'], 45)
        self.assertEqual(term_res['remaining_minutes'], 42)

        # 3. Verify CallRecord exists in database
        record = CallRecord.objects.get(call_id=term_res['call_id'])
        self.assertEqual(record.student, self.student)
        self.assertEqual(record.destination_number, '+919876543210')
        self.assertEqual(record.minutes_deducted, 3)
        self.assertEqual(record.call_status, 'Completed')

    def test_call_session_unauthorized_number_rejected(self):
        from .calling_services import CallSessionManager

        # Initiate session with non-whitelisted number
        init_res = CallSessionManager.initiate_session(self.student.calling_code, '+919999999999', 'DEV-BOOTH-1')
        self.assertFalse(init_res['authorized'])
        self.assertIn('Unauthorized number', init_res['reason'])

    def test_enterprise_models_crud(self):
        from .models import SchoolAdminProfile, CampusSubscription, FinancialTransaction, SystemAuditLog, PlatformSetting

        # Profile
        profile = SchoolAdminProfile.objects.create(
            school=self.school,
            admin_id='ADM-TEST-1',
            name='Dr. Test Admin',
            email='testadmin@test.edu',
            phone='+919810012345'
        )
        self.assertEqual(profile.status, 'Active')

        # Subscription
        sub = CampusSubscription.objects.create(
            subscription_id='SUB-TEST-100',
            school=self.school,
            tier='Enterprise Boarding',
            contract_value=150000.00,
            expiry_date=timezone.now().date() + timedelta(days=365)
        )
        self.assertEqual(sub.status, 'Active')

        # Financial Transaction
        txn = FinancialTransaction.objects.create(
            transaction_id='TXN-TEST-500',
            school=self.school,
            category='Annual Subscription',
            amount=150000.00,
            payment_method='NEFT / RTGS',
            status='Successful'
        )
        self.assertEqual(txn.status, 'Successful')

        # System Audit Log
        audit = SystemAuditLog.objects.create(
            actor='Super Admin',
            action_type='CREATE',
            target_domain='Subscription',
            target_id=sub.subscription_id,
            description='Provisioned Enterprise Boarding subscription'
        )
        self.assertEqual(audit.action_type, 'CREATE')

        # Platform Settings
        setting = PlatformSetting.get_settings()
        self.assertIsNotNone(setting.platform_title)


class SuperAdminCitadelBackendTests(TestCase):
    """
    Division II automated verification:
    Validates all 18 Super Admin Citadel endpoints across Phase 1 - Phase 5.
    """
    def setUp(self):
        self.admin_user, _ = User.objects.get_or_create(username='admin', defaults={'email': 'admin@s2d.com', 'is_superuser': True, 'is_staff': True})
        self.admin_user.is_superuser = True
        self.admin_user.is_staff = True
        self.admin_user.save()

        self.client = Client()
        self.client.force_login(self.admin_user)

        self.school = School.objects.create(
            code='SCH-CITADEL-01',
            name='Citadel International Academy',
            city='Dehradun',
            admin_name='Dean Vance',
            admin_email='dean@citadel.edu',
            admin_phone='+919810011223'
        )

    def test_phase1_school_admins_workflow(self):
        # 1. Directory
        resp = self.client.get('/super-admin/school-admins/')
        self.assertEqual(resp.status_code, 200)

        # 2. Add
        add_resp = self.client.post('/super-admin/school-admins/add.html', {
            'name': 'Dr. Alistair Finch',
            'designation': 'Campus Principal',
            'email': 'a.finch@citadel.edu',
            'phone': '+91 98111 88990',
            'school_id': self.school.code,
            'require_mfa': 'on'
        })
        self.assertEqual(add_resp.status_code, 302)

        from .models import SchoolAdminProfile
        profile = SchoolAdminProfile.objects.filter(email='a.finch@citadel.edu').first()
        self.assertIsNotNone(profile)
        self.assertEqual(profile.name, 'Dr. Alistair Finch')
        self.assertEqual(profile.school, self.school)
        self.assertTrue(profile.mfa_enforced)

        # 3. Edit
        edit_resp = self.client.post(f'/super-admin/school-admins/edit.html?id={profile.admin_id}', {
            'id': profile.admin_id,
            'name': 'Dr. Alistair Finch (Senior Dean)',
            'designation': 'Senior Dean of Academics',
            'email': 'a.finch@citadel.edu',
            'phone': '+91 98111 88990',
            'school': self.school.name,
            'status': 'Active'
        })
        self.assertEqual(edit_resp.status_code, 302)
        profile.refresh_from_db()
        self.assertEqual(profile.name, 'Dr. Alistair Finch (Senior Dean)')

        # 4. Details
        det_resp = self.client.get(f'/super-admin/school-admins/details.html?id={profile.admin_id}')
        self.assertEqual(det_resp.status_code, 200)

    def test_phase2_devices_workflow(self):
        # 1. Device list
        resp = self.client.get('/super-admin/devices/')
        self.assertEqual(resp.status_code, 200)

        # 2. Register device
        reg_resp = self.client.post('/super-admin/devices/register.html', {
            'deviceName': 'South Wing Kiosk 01',
            'serialNumber': 'SN-SOUTH-001',
            'imei': '864298039988776',
            'school': self.school.code,
            'wingLocation': 'South Hostel Wing',
            'status': 'Online'
        })
        self.assertEqual(reg_resp.status_code, 302)

        from .models import KioskDevice
        dev = KioskDevice.objects.filter(serial_number='SN-SOUTH-001').first()
        self.assertIsNotNone(dev)
        self.assertEqual(dev.name, 'South Wing Kiosk 01')
        self.assertEqual(dev.school, self.school)

        # 3. Details
        det_resp = self.client.get(f'/super-admin/devices/details.html?id={dev.device_id}')
        self.assertEqual(det_resp.status_code, 200)

    def test_phase3_subscriptions_and_payments_workflow(self):
        # 1. Subscriptions overview
        resp = self.client.get('/super-admin/subscriptions/')
        self.assertEqual(resp.status_code, 200)

        # 2. Create subscription
        create_resp = self.client.post('/super-admin/subscriptions/create.html', {
            'school': self.school.code,
            'planName': 'Enterprise Boarding Annual (₹8,40,000)',
            'studentSeats': 600,
            'deviceSeats': 20,
            'expiryDate': '2027-12-31'
        })
        self.assertEqual(create_resp.status_code, 302)

        from .models import CampusSubscription, FinancialTransaction
        sub = CampusSubscription.objects.filter(school=self.school).order_by('-id').first()
        self.assertIsNotNone(sub)
        self.assertEqual(sub.student_seats, 600)

        # Verify auto-generated transaction
        txn = FinancialTransaction.objects.filter(school=self.school, category='Annual Subscription').order_by('-id').first()
        self.assertIsNotNone(txn)
        self.assertEqual(float(txn.amount), 840000.00)

        # 3. Payments overview & details
        pay_resp = self.client.get('/super-admin/payments/')
        self.assertEqual(pay_resp.status_code, 200)

        det_resp = self.client.get(f'/super-admin/payments/details.html?id={txn.transaction_id}')
        self.assertEqual(det_resp.status_code, 200)

    def test_phase4_call_history_and_reports_workflow(self):
        # 1. Call history
        ch_resp = self.client.get('/super-admin/call-history/')
        self.assertEqual(ch_resp.status_code, 200)

        # 2. Reports overview
        rep_resp = self.client.get('/super-admin/reports/')
        self.assertEqual(rep_resp.status_code, 200)

        # 3. CSV export
        csv_resp = self.client.get('/super-admin/reports/export.csv')
        self.assertEqual(csv_resp.status_code, 200)
        self.assertEqual(csv_resp['Content-Type'], 'text/csv')
        self.assertIn(b'Campus Name', csv_resp.content)

    def test_phase5_governance_and_settings_workflow(self):
        # 1. Roles & permissions
        role_resp = self.client.get('/super-admin/roles-permissions/')
        self.assertEqual(role_resp.status_code, 200)

        role_post = self.client.post('/super-admin/roles-permissions/list.html', {})
        self.assertEqual(role_post.status_code, 302)

        role_create_post = self.client.post('/super-admin/roles-permissions/create.html', {
            'role_name': 'Hostel Night In-Charge'
        })
        self.assertEqual(role_create_post.status_code, 302)

        # 2. Settings general
        set_gen_resp = self.client.get('/super-admin/settings/general.html')
        self.assertEqual(set_gen_resp.status_code, 200)

        set_gen_post = self.client.post('/super-admin/settings/general.html', {
            'platform_name': 'Source 2 Destination Enterprise Cloud',
            'support_email': 'support@s2dcloud.io'
        })
        self.assertEqual(set_gen_post.status_code, 302)

        from .models import PlatformSetting
        plat = PlatformSetting.get_settings()
        self.assertEqual(plat.platform_title, 'Source 2 Destination Enterprise Cloud')

        # 3. Settings notifications
        set_notif_resp = self.client.get('/super-admin/settings/notifications.html')
        self.assertEqual(set_notif_resp.status_code, 200)

        set_notif_post = self.client.post('/super-admin/settings/notifications.html', {
            'sms_sender_id': 'S2DALERT',
            'threshold': 20
        })
        self.assertEqual(set_notif_post.status_code, 302)

        plat.refresh_from_db()
        self.assertEqual(plat.sms_sender_id, 'S2DALERT')
        self.assertEqual(plat.low_balance_threshold_minutes, 20)

        # 4. Audit logs
        audit_resp = self.client.get('/super-admin/settings/audit-logs.html')
        self.assertEqual(audit_resp.status_code, 200)


