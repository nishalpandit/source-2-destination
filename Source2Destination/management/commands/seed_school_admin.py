"""
Management command to purge legacy/duplicate static seed data for the School Admin tenant
(SCH-1001) and implant a fresh, cohesive, authentic Indian residential campus dataset.

Usage:
    python manage.py seed_school_admin
"""
from datetime import time, timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from Source2Destination.models import (
    School, AcademicClass, ClassSection, Student, Guardian, StudentStatusLog,
    CampusDurationRule, CallingScheduleRule, StudentScheduleException,
    RechargePlan, StudentRecharge, CallRecord, KioskDevice, DeviceAssignment, HostelWarden
)


class Command(BaseCommand):
    help = "Implant fresh, authentic live database data for the School Admin portal (SCH-1001)."

    @transaction.atomic
    def handle(self, *args, **options):
        now = timezone.now()
        today = timezone.localdate()

        # 1. Ensure School Tenant SCH-1001 with Complete Indian Profile & Settings
        school, _ = School.objects.update_or_create(
            code='SCH-1001',
            defaults={
                'name': 'Doon Valley Residential Academy',
                'campus_type': 'Co-ed Residential Boarding',
                'affiliation_board': 'CBSE',
                'website': 'https://www.doonvalley.edu.in',
                'city': 'Dehradun, Uttarakhand',
                'state': 'Uttarakhand',
                'postal_code': '248001',
                'country': 'India',
                'address': 'Rajpur Road, Mussoorie Foothills, Dehradun 248001',
                'timezone': 'Asia/Kolkata',
                'hostel_blocks_count': 4,
                'admin_name': 'Dr. Ramesh Chandra Sharma',
                'admin_email': 'principal@doonvalley.edu.in',
                'admin_phone': '+91 98101 23456',
                'secondary_contact_name': 'Major Rajeshwar Singh (Retd.)',
                'secondary_contact_email': 'wardens@doonvalley.edu.in',
                'secondary_contact_phone': '+91 98101 23481',
                'daily_duration_cap': 15,
                'calling_window_start': time(17, 0),
                'calling_window_end': time(19, 30),
                'allowed_calling_days': 'All 7 Days',
                'emergency_calling_allowed': True,
                'kiosk_group_tag': 'AE-DOON-HOSTEL-BOOTH',
                'display_school_caller_id': True,
                'show_guardian_whitelist_numbers': False,
                'emergency_override_caller_id': True,
                'primary_emergency_phone': '+91 98101 99100',
                'secondary_emergency_phone': '+91 98101 99101',
                'warden_escalation_phone': '+91 98101 99102',
                'notify_sms_guardians': True,
                'notify_email_recharges': True,
                'notify_push_validity': True,
                'status': 'Active',
            }
        )

        # 2. Purge stale/duplicate SCH-1001 child records cleanly
        CallRecord.objects.filter(school=school).delete()
        StudentRecharge.objects.filter(school=school).delete()
        DeviceAssignment.objects.filter(school=school).delete()
        KioskDevice.objects.filter(school=school).delete()
        HostelWarden.objects.filter(school=school).delete()
        StudentScheduleException.objects.filter(student__school=school).delete()
        CallingScheduleRule.objects.filter(school=school).delete()
        CampusDurationRule.objects.filter(school=school).delete()
        StudentStatusLog.objects.filter(school=school).delete()
        Guardian.objects.filter(school=school).delete()
        Student.objects.filter(school=school).delete()
        ClassSection.objects.filter(school=school).delete()
        AcademicClass.objects.filter(school=school).delete()

        # 3. Academic Classes (Grade 7 - Grade 12) & Sections (A, B)
        class_specs = [
            ('CLS-07', 'Grade 7', 'Smt. Kavita Joshi', 12, 'Junior Wing Window', 'Ashoka Junior Wing', 'DEV-DV-05'),
            ('CLS-08', 'Grade 8', 'Shri Arvind Kulkarni', 12, 'Junior Wing Window', 'Ashoka Junior Wing', 'DEV-DV-05'),
            ('CLS-09', 'Grade 9', 'Dr. Nandini Tiwari', 15, 'Standard Hostel Window', 'Sarojini Sadan', 'DEV-DV-03'),
            ('CLS-10', 'Grade 10', 'Shri Pradeep Rawat', 15, 'Standard Hostel Window', 'Tagore Bhavan', 'DEV-DV-01'),
            ('CLS-11', 'Grade 11', 'Smt. Vandana Menon', 15, 'Senior Wing Window', 'Vivekananda House', 'DEV-DV-04'),
            ('CLS-12', 'Grade 12', 'Prof. Raghavendra Nair', 20, 'Senior Wing Window', 'Tagore Bhavan', 'DEV-DV-02'),
        ]
        classes_by_name = {}
        for code, name, supervisor, daily_min, sched_grp, wing, booth in class_specs:
            cls_obj = AcademicClass.objects.create(
                school=school,
                code=code,
                name=name,
                supervisor=supervisor,
                default_daily_minutes=daily_min,
                schedule_group=sched_grp,
                status='Active',
            )
            classes_by_name[name] = cls_obj
            for sec_letter, floor in [('A', 'Floor 1'), ('B', 'Floor 2')]:
                ClassSection.objects.create(
                    academic_class=cls_obj,
                    school=school,
                    code=f"SEC-{code[-2:]}{sec_letter}",
                    name=f"Section {sec_letter}",
                    room_wing=f"{wing} · {floor}",
                    advisor=supervisor,
                    assigned_booth=booth,
                    status='Active',
                )

        # 4. Hostel Wardens (4 clean, distinct Indian wardens)
        warden_specs = [
            ('WRD-DV-101', 'Major Rajeshwar Singh (Retd.)', '+91 98101 23481', 'r.singh@doonvalley.edu.in', 'Tagore Bhavan (Senior Boys)', '16:00 – 00:00', 2, 'On Duty'),
            ('WRD-DV-102', 'Smt. Meenakshi Rawat', '+91 98101 23482', 'm.rawat@doonvalley.edu.in', 'Sarojini Sadan (Girls Wing)', '15:30 – 23:30', 2, 'On Duty'),
            ('WRD-DV-103', 'Subedar Harish Negi', '+91 98101 23483', 'h.negi@doonvalley.edu.in', 'Vivekananda House', '16:00 – 23:00', 1, 'On Duty'),
            ('WRD-DV-104', 'Shri Deepak Bisht', '+91 98101 23484', 'd.bisht@doonvalley.edu.in', 'Ashoka Junior Wing', '08:00 – 16:00', 1, 'Off Duty'),
        ]
        for code, name, phone, email, block, shift, booths, status in warden_specs:
            HostelWarden.objects.create(
                code=code,
                school=school,
                name=name,
                phone=phone,
                email=email,
                hostel_block=block,
                shift_timings=shift,
                booths_monitored=booths,
                status=status,
            )

        # 5. Enrolled Kiosk Booths (6 devices: 5 Online, 1 Maintenance) & Device Assignments
        kiosk_specs = [
            ('DEV-DV-01', 'Tagore Bhavan Booth 1', 'SN-DV-8801', 'Tagore Bhavan (Senior Boys)', 'Grade 10 & Grade 12', 'Online', 2),
            ('DEV-DV-02', 'Tagore Bhavan Booth 2', 'SN-DV-8802', 'Tagore Bhavan (Senior Boys)', 'Grade 12 Boarders', 'Online', 4),
            ('DEV-DV-03', 'Sarojini Sadan Booth 1', 'SN-DV-8803', 'Sarojini Sadan (Girls Wing)', 'Grade 9 – Grade 12 Girls', 'Online', 1),
            ('DEV-DV-04', 'Vivekananda House Booth 1', 'SN-DV-8804', 'Vivekananda House', 'Grade 11 Science & Commerce', 'Online', 3),
            ('DEV-DV-05', 'Ashoka Junior Wing Booth 1', 'SN-DV-8805', 'Ashoka Junior Wing', 'Grade 7 & Grade 8', 'Online', 5),
            ('DEV-DV-06', 'Sarojini Sadan Backup Booth', 'SN-DV-8806', 'Sarojini Sadan (Girls Wing)', 'Shared Reserve Pool', 'Maintenance', 180),
        ]
        kiosks = []
        for dev_id, name, sn, block, wing_cohort, status, hb_mins in kiosk_specs:
            k = KioskDevice.objects.create(
                device_id=dev_id,
                school=school,
                name=name,
                serial_number=sn,
                app_version='v3.1.4-enterprise',
                hostel_block=block,
                assigned_wing=wing_cohort,
                status=status,
                last_heartbeat=now - timedelta(minutes=hb_mins),
            )
            kiosks.append(k)
            DeviceAssignment.objects.create(
                school=school,
                device=k,
                academic_class=wing_cohort,
                hostel_wing=block,
                assigned_by='Dr. Ramesh Chandra Sharma',
                assigned_date=today - timedelta(days=20),
                status='Active' if status == 'Online' else 'Maintenance',
            )

        # 6. Fresh Cohort of 24 Indian Boarding Students & 24 Verified Guardians
        student_roster = [
            # (name, gender, grade, sec, wing, father, mother, phone_suffix, mins, daily_cap, expiry_offset_days, status)
            ('Aarav Deshmukh', 'Male', 'Grade 12', 'Section A', 'Tagore Bhavan · Rm 301', 'Prakash Deshmukh', 'Sujata Deshmukh', '101', 260, 20, 140, 'Active'),
            ('Diya Malhotra', 'Female', 'Grade 12', 'Section A', 'Sarojini Sadan · Rm 204', 'Rajiv Malhotra', 'Neha Malhotra', '102', 310, 20, 165, 'Active'),
            ('Rohan Kulkarni', 'Male', 'Grade 12', 'Section B', 'Tagore Bhavan · Rm 308', 'Suresh Kulkarni', 'Anjali Kulkarni', '103', 195, 20, 120, 'Active'),
            ('Ishita Chatterjee', 'Female', 'Grade 12', 'Section B', 'Sarojini Sadan · Rm 211', 'Subhash Chatterjee', 'Moumita Chatterjee', '104', 240, 20, 95, 'Active'),

            ('Vihaan Kapoor', 'Male', 'Grade 11', 'Section A', 'Vivekananda House · Rm 114', 'Vikram Kapoor', 'Ritika Kapoor', '105', 180, 15, 110, 'Active'),
            ('Ananya Iyer', 'Female', 'Grade 11', 'Section A', 'Sarojini Sadan · Rm 109', 'Karthik Iyer', 'Lakshmi Iyer', '106', 225, 15, 130, 'Active'),
            ('Siddharth Bansal', 'Male', 'Grade 11', 'Section B', 'Vivekananda House · Rm 118', 'Manoj Bansal', 'Pooja Bansal', '107', 145, 15, 9, 'Active'),  # Expiring soon
            ('Meera Nair', 'Female', 'Grade 11', 'Section B', 'Sarojini Sadan · Rm 112', 'Venugopal Nair', 'Deepa Nair', '108', 290, 15, 155, 'Active'),

            ('Kabir Verma', 'Male', 'Grade 10', 'Section A', 'Tagore Bhavan · Rm 202', 'Amitabh Verma', 'Shalini Verma', '109', 210, 15, 85, 'Active'),
            ('Saanvi Agarwal', 'Female', 'Grade 10', 'Section A', 'Sarojini Sadan · Rm 105', 'Sanjay Agarwal', 'Meera Agarwal', '110', 175, 15, 100, 'Active'),
            ('Arjun Chauhan', 'Male', 'Grade 10', 'Section B', 'Tagore Bhavan · Rm 209', 'Devendra Chauhan', 'Rekha Chauhan', '111', 150, 15, 6, 'Active'),  # Expiring soon
            ('Riya Sengupta', 'Female', 'Grade 10', 'Section B', 'Sarojini Sadan · Rm 108', 'Anirban Sengupta', 'Debjani Sengupta', '112', 205, 15, 125, 'Active'),

            ('Devansh Joshi', 'Male', 'Grade 9', 'Section A', 'Vivekananda House · Rm 102', 'Harish Joshi', 'Sunita Joshi', '113', 165, 15, 90, 'Active'),
            ('Kavya Reddy', 'Female', 'Grade 9', 'Section A', 'Sarojini Sadan · Rm 101', 'Srinivas Reddy', 'Padma Reddy', '114', 230, 15, 115, 'Active'),
            ('Nikhil Thakur', 'Male', 'Grade 9', 'Section B', 'Vivekananda House · Rm 106', 'Rajendra Thakur', 'Seema Thakur', '115', 130, 15, 70, 'Active'),
            ('Tanvi Saxena', 'Female', 'Grade 9', 'Section B', 'Sarojini Sadan · Rm 104', 'Alok Saxena', 'Ritu Saxena', '116', 190, 15, 105, 'Active'),

            ('Yashvardhan Rana', 'Male', 'Grade 8', 'Section A', 'Ashoka Junior Wing · Rm 12', 'Mahendra Rana', 'Kiran Rana', '117', 140, 12, 80, 'Active'),
            ('Aditi Bhatt', 'Female', 'Grade 8', 'Section A', 'Ashoka Junior Wing · Rm 15', 'Girish Bhatt', 'Alka Bhatt', '118', 160, 12, 95, 'Active'),
            ('Pranav Shukla', 'Male', 'Grade 8', 'Section B', 'Ashoka Junior Wing · Rm 19', 'Dinesh Shukla', 'Mamta Shukla', '119', 115, 12, 60, 'Active'),
            ('Nisha Tiwari', 'Female', 'Grade 8', 'Section B', 'Ashoka Junior Wing · Rm 22', 'Rakesh Tiwari', 'Geeta Tiwari', '120', 0, 12, -10, 'Inactive'),

            ('Reyansh Mehra', 'Male', 'Grade 7', 'Section A', 'Ashoka Junior Wing · Rm 03', 'Pankaj Mehra', 'Sonia Mehra', '121', 125, 12, 75, 'Active'),
            ('Myra Sinha', 'Female', 'Grade 7', 'Section A', 'Ashoka Junior Wing · Rm 06', 'Abhishek Sinha', 'Priyanka Sinha', '122', 155, 12, 110, 'Active'),
            ('Shaurya Gill', 'Male', 'Grade 7', 'Section B', 'Ashoka Junior Wing · Rm 08', 'Harpreet Gill', 'Simran Gill', '123', 135, 12, 85, 'Active'),
            ('Aanya Kashyap', 'Female', 'Grade 7', 'Section B', 'Ashoka Junior Wing · Rm 10', 'Vinod Kashyap', 'Nidhi Kashyap', '124', 0, 12, -15, 'Inactive'),
        ]

        students = []
        guardians_by_student = {}
        for idx, row in enumerate(student_roster, start=1):
            (name, gender, grade, sec, wing, father, mother, suffix, mins, daily_cap, exp_days, status) = row
            f_phone = f"+91 98110 40{suffix}"
            m_phone = f"+91 98110 50{suffix}"
            e_phone = f"+91 98110 60{suffix}"
            s_code = f"STU-DV-{1000 + idx}"
            call_code = f"S2D-DV-{2000 + idx}"

            stu = Student.objects.create(
                code=s_code,
                calling_code=call_code,
                school=school,
                name=name,
                gender=gender,
                class_name=grade,
                section=sec,
                roll_number=f"DV26-{idx:03d}",
                hostel_wing=wing,
                guardian_name=father,
                guardian_relation='Father',
                primary_phone=f_phone,
                secondary_phone=m_phone,
                remaining_minutes=mins,
                daily_limit_min=daily_cap,
                wallet_balance=Decimal(str(mins * 2)),
                validity_start=today - timedelta(days=45),
                validity_expiry=today + timedelta(days=exp_days),
                pin=f"{1400 + idx}",
                code_status='Active' if status == 'Active' else 'Suspended',
                code_last_used=now - timedelta(hours=(idx % 12) + 1) if status == 'Active' else None,
                status=status,
            )
            students.append(stu)

            g = Guardian.objects.create(
                school=school,
                student=stu,
                code=f"GRD-DV-{1000 + idx}",
                name=father,
                relation='Father',
                father_phone=f_phone,
                mother_phone=m_phone,
                emergency_phone=e_phone,
                email=f"{father.lower().replace(' ', '.')}@gmail.com",
                verification='KYC Verified (Aadhaar)',
                whitelist_status='Authorized (3 Numbers)',
                status='Active' if status == 'Active' else 'Inactive',
            )
            guardians_by_student[stu.id] = g

        # 7. Calling Duration Rules, Schedules & Student Exceptions
        CampusDurationRule.objects.create(
            school=school,
            scope='School-Wide Default',
            max_call_duration=15,
            daily_cumulative_limit=15,
        )
        CampusDurationRule.objects.create(
            school=school,
            scope='Senior Wing (Grade 12)',
            academic_class=classes_by_name['Grade 12'],
            max_call_duration=20,
            daily_cumulative_limit=20,
        )

        CallingScheduleRule.objects.create(
            school=school,
            name='Weekday Evening Calling Window',
            days_of_week='MON,TUE,WED,THU,FRI',
            start_time=time(17, 0),
            end_time=time(19, 30),
            policy_type='allowed',
            is_active=True,
        )
        CallingScheduleRule.objects.create(
            school=school,
            name='Weekend Morning Family Window',
            days_of_week='SAT,SUN',
            start_time=time(9, 0),
            end_time=time(11, 30),
            policy_type='allowed',
            is_active=True,
        )
        CallingScheduleRule.objects.create(
            school=school,
            name='Night Lights-Out Curfew',
            days_of_week='MON,TUE,WED,THU,FRI,SAT,SUN',
            start_time=time(21, 30),
            end_time=time(6, 30),
            policy_type='restricted',
            is_active=True,
        )

        StudentScheduleException.objects.create(
            student=students[1],
            allowed_window='06:30 – 07:15',
            valid_until=today + timedelta(days=90),
            reason='Parent stationed in London (GMT timezone exception)',
        )
        StudentScheduleException.objects.create(
            student=students[5],
            allowed_window='20:15 – 20:45',
            valid_until=today + timedelta(days=60),
            reason='Parent stationed in Singapore (SGT timezone exception)',
        )

        # 8. Standardized INR Recharge Plans & 18 Student Recharges
        plan_specs = [
            ('RPL-INR-01', 'Weekend Calling Pass', Decimal('199.00'), 120, 30, 12, 'STARTER'),
            ('RPL-INR-02', 'Monthly Hostel Pack', Decimal('499.00'), 350, 30, 15, 'MOST POPULAR'),
            ('RPL-INR-03', 'Quarterly Term Pack', Decimal('999.00'), 800, 90, 15, 'TERM VALUE'),
            ('RPL-INR-04', 'Annual Boarding Pack', Decimal('1499.00'), 1400, 180, 20, 'ANNUAL'),
        ]
        plans = []
        for p_code, p_name, price, mins_alloc, val_days, cap, badge in plan_specs:
            plan_obj, _ = RechargePlan.objects.update_or_create(
                code=p_code,
                defaults={
                    'name': p_name,
                    'price': price,
                    'minutes_allocated': mins_alloc,
                    'validity_days': val_days,
                    'per_call_cap': cap,
                    'badge_text': badge,
                    'status': 'Active',
                }
            )
            plans.append(plan_obj)

        for i in range(18):
            stu = students[i % 22]
            plan = plans[i % len(plans)]
            StudentRecharge.objects.create(
                recharge_id=f"RCG-DV-2026-{3001 + i}",
                student=stu,
                school=school,
                plan=plan,
                plan_name_cache=plan.name,
                amount=plan.price,
                minutes_added=plan.minutes_allocated,
                validity_days_added=plan.validity_days,
                payment_mode='UPI Parent Portal' if i % 2 == 0 else 'Campus Bursar Desk',
                voucher_ref=f"DOON-DESK-2026-{501 + i}",
                status='Successful',
                created_at=now - timedelta(days=(i % 25), hours=(i % 6) + 1),
            )

        # 9. Fresh Live Call Records across ALL 7 Days (including Today) + 30-day Grade Usage
        # Daily pattern: (days_ago, completed_count, restricted_count)
        seven_day_pattern = [
            (6, 9, 1),
            (5, 11, 2),
            (4, 15, 1),
            (3, 18, 2),
            (2, 10, 1),
            (1, 12, 1),
            (0, 14, 2),  # Today: 16 total calls (14 Completed, 2 Restricted)
        ]

        active_students = [s for s in students if s.status == 'Active']
        call_seq = 1001
        for days_ago, comp_cnt, rest_cnt in seven_day_pattern:
            base_dt = now - timedelta(days=days_ago)
            for j in range(comp_cnt):
                stu = active_students[(call_seq + j) % len(active_students)]
                grd = guardians_by_student[stu.id]
                # Give higher grades slightly longer realistic calls
                grade_num = int(stu.class_name.split()[-1])
                mins = 6 + ((grade_num - 6) * 2) + (j % 4)
                secs = mins * 60 + ((j * 17) % 55)
                call_dt = base_dt.replace(hour=17 + (j % 2), minute=(j * 4) % 58, second=12)
                if days_ago == 0 and call_dt > now:
                    call_dt = now - timedelta(minutes=(j + 1) * 8)

                CallRecord.objects.create(
                    call_id=f"CAL-DV-{call_seq}",
                    school=school,
                    student=stu,
                    guardian=grd,
                    destination_number=stu.primary_phone if j % 3 != 0 else (stu.secondary_phone or stu.primary_phone),
                    call_type='Father' if j % 3 != 0 else 'Mother',
                    device_id=kiosks[j % 5].name,
                    start_time=call_dt,
                    end_time=call_dt + timedelta(seconds=secs),
                    duration_seconds=secs,
                    minutes_deducted=mins,
                    call_status='Completed',
                )
                call_seq += 1

            for k_idx in range(rest_cnt):
                stu = active_students[(call_seq + k_idx) % len(active_students)]
                grd = guardians_by_student[stu.id]
                call_dt = base_dt.replace(hour=14, minute=15 + k_idx * 10, second=0)
                if days_ago == 0 and call_dt > now:
                    call_dt = now - timedelta(minutes=15 + k_idx * 5)

                CallRecord.objects.create(
                    call_id=f"CAL-DV-{call_seq}",
                    school=school,
                    student=stu,
                    guardian=grd,
                    destination_number=stu.primary_phone,
                    call_type='Father',
                    device_id=kiosks[k_idx % 5].name,
                    start_time=call_dt,
                    end_time=call_dt,
                    duration_seconds=0,
                    minutes_deducted=0,
                    call_status='Restricted Schedule',
                )
                call_seq += 1

        # Update denormalized school counters cleanly
        school.enrolled_students = len(students)
        school.active_students = len(active_students)
        school.device_count = len(kiosks)
        school.save(update_fields=['enrolled_students', 'active_students', 'device_count'])

        self.stdout.write(self.style.SUCCESS(
            f"Implanted fresh live data for {school.code} ({school.name}): "
            f"{len(class_specs)} classes, {len(students)} students, {len(warden_specs)} wardens, "
            f"{len(kiosks)} kiosks, {call_seq - 1001} call records, 18 recharges."
        ))
