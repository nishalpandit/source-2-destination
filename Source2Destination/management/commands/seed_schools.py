import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from Source2Destination.models import Franchise, School, Student

INITIAL_STUDENTS = [
    {
        "code": "STU-4001",
        "calling_code": "S2D-OAK-8841",
        "name": "Liam Hawthorne",
        "school_code": "SCH-1001",
        "class_name": "Grade 10",
        "section": "Section A",
        "roll_number": "10-A-14",
        "hostel_wing": "North Hall · Rm 204",
        "guardian_name": "Robert Hawthorne",
        "guardian_relation": "Father",
        "primary_phone": "+1 (555) 801-2210",
        "secondary_phone": "+1 (555) 801-2211",
        "remaining_minutes": 142,
        "daily_limit_min": 15,
        "wallet_balance": 65.00,
        "validity_start": "2026-08-01",
        "validity_expiry": "2027-05-31",
        "status": "Active"
    },
    {
        "code": "STU-4002",
        "calling_code": "S2D-OAK-8842",
        "name": "Clara Bennett",
        "school_code": "SCH-1001",
        "class_name": "Grade 9",
        "section": "Section B",
        "roll_number": "09-B-08",
        "hostel_wing": "East Gables · Rm 112",
        "guardian_name": "Margaret Bennett",
        "guardian_relation": "Mother",
        "primary_phone": "+1 (555) 802-3490",
        "secondary_phone": "+1 (555) 802-3499",
        "remaining_minutes": 98,
        "daily_limit_min": 15,
        "wallet_balance": 45.00,
        "validity_start": "2026-08-01",
        "validity_expiry": "2027-05-31",
        "status": "Active"
    },
    {
        "code": "STU-4003",
        "calling_code": "S2D-OAK-8843",
        "name": "Noah Montgomery",
        "school_code": "SCH-1001",
        "class_name": "Grade 11",
        "section": "Section A",
        "roll_number": "11-A-21",
        "hostel_wing": "North Hall · Rm 308",
        "guardian_name": "David Montgomery",
        "guardian_relation": "Father",
        "primary_phone": "+1 (555) 803-5120",
        "secondary_phone": "+1 (555) 803-5125",
        "remaining_minutes": 18,
        "daily_limit_min": 12,
        "wallet_balance": 15.00,
        "validity_start": "2026-05-15",
        "validity_expiry": "2026-11-18",
        "status": "Active"
    },
    {
        "code": "STU-4004",
        "calling_code": "S2D-OAK-8844",
        "name": "Amelia Fletcher",
        "school_code": "SCH-1001",
        "class_name": "Grade 12",
        "section": "Section C",
        "roll_number": "12-C-05",
        "hostel_wing": "East Gables · Rm 305",
        "guardian_name": "Evelyn Fletcher",
        "guardian_relation": "Mother",
        "primary_phone": "+1 (555) 804-7740",
        "secondary_phone": "+1 (555) 804-7741",
        "remaining_minutes": 215,
        "daily_limit_min": 20,
        "wallet_balance": 85.00,
        "validity_start": "2026-08-10",
        "validity_expiry": "2027-06-15",
        "status": "Active"
    },
    {
        "code": "STU-4005",
        "calling_code": "S2D-OAK-8845",
        "name": "Oliver Kingsley",
        "school_code": "SCH-1001",
        "class_name": "Grade 8",
        "section": "Section A",
        "roll_number": "08-A-03",
        "hostel_wing": "Junior Wing · Rm 105",
        "guardian_name": "Henry Kingsley",
        "guardian_relation": "Father",
        "primary_phone": "+1 (555) 805-1192",
        "secondary_phone": "+1 (555) 805-1198",
        "remaining_minutes": 0,
        "daily_limit_min": 10,
        "wallet_balance": 0.00,
        "validity_start": "2026-04-01",
        "validity_expiry": "2026-10-31",
        "status": "Inactive"
    },
    {
        "code": "STU-4006",
        "calling_code": "S2D-OAK-8846",
        "name": "Sophia Whitaker",
        "school_code": "SCH-1001",
        "class_name": "Grade 10",
        "section": "Section B",
        "roll_number": "10-B-19",
        "hostel_wing": "East Gables · Rm 214",
        "guardian_name": "Catherine Whitaker",
        "guardian_relation": "Legal Guardian",
        "primary_phone": "+1 (555) 806-6631",
        "secondary_phone": "+1 (555) 806-6639",
        "remaining_minutes": 64,
        "daily_limit_min": 15,
        "wallet_balance": 35.00,
        "validity_start": "2026-06-01",
        "validity_expiry": "2026-11-22",
        "status": "Active"
    },
    {
        "code": "STU-4007",
        "calling_code": "S2D-WST-5510",
        "name": "Ethan Gallagher",
        "school_code": "SCH-1002",
        "class_name": "Grade 11",
        "section": "Section A",
        "roll_number": "11-A-09",
        "hostel_wing": "Beacon Block · Rm 402",
        "guardian_name": "Patrick Gallagher",
        "guardian_relation": "Father",
        "primary_phone": "+1 (555) 811-4402",
        "secondary_phone": "+1 (555) 811-4409",
        "remaining_minutes": 175,
        "daily_limit_min": 15,
        "wallet_balance": 70.00,
        "validity_start": "2026-08-15",
        "validity_expiry": "2027-05-30",
        "status": "Active"
    },
    {
        "code": "STU-4008",
        "calling_code": "S2D-WST-5511",
        "name": "Maya Sullivan",
        "school_code": "SCH-1002",
        "class_name": "Grade 9",
        "section": "Section C",
        "roll_number": "09-C-15",
        "hostel_wing": "Harbor Wing · Rm 118",
        "guardian_name": "Laura Sullivan",
        "guardian_relation": "Mother",
        "primary_phone": "+1 (555) 812-9087",
        "secondary_phone": "+1 (555) 812-9088",
        "remaining_minutes": 112,
        "daily_limit_min": 15,
        "wallet_balance": 50.00,
        "validity_start": "2026-08-15",
        "validity_expiry": "2027-05-30",
        "status": "Active"
    },
    {
        "code": "STU-4009",
        "calling_code": "S2D-STJ-3301",
        "name": "Lucas Pritchard",
        "school_code": "SCH-1003",
        "class_name": "Grade 12",
        "section": "Section A",
        "roll_number": "12-A-04",
        "hostel_wing": "St. Bede Hall · Rm 201",
        "guardian_name": "Alan Pritchard",
        "guardian_relation": "Father",
        "primary_phone": "+1 (555) 820-3100",
        "secondary_phone": "+1 (555) 820-3105",
        "remaining_minutes": 28,
        "daily_limit_min": 12,
        "wallet_balance": 20.00,
        "validity_start": "2026-05-20",
        "validity_expiry": "2026-11-20",
        "status": "Active"
    },
    {
        "code": "STU-4010",
        "calling_code": "S2D-GRN-9104",
        "name": "Chloe Takahashi",
        "school_code": "SCH-1004",
        "class_name": "Grade 10",
        "section": "Section A",
        "roll_number": "10-A-17",
        "hostel_wing": "Cascade Dorm · Rm 310",
        "guardian_name": "Kenji Takahashi",
        "guardian_relation": "Father",
        "primary_phone": "+1 (555) 831-7022",
        "secondary_phone": "+1 (555) 831-7023",
        "remaining_minutes": 240,
        "daily_limit_min": 20,
        "wallet_balance": 90.00,
        "validity_start": "2026-09-01",
        "validity_expiry": "2027-06-30",
        "status": "Active"
    },
    {
        "code": "STU-4011",
        "calling_code": "S2D-OAK-8847",
        "name": "Benjamin Mercer",
        "school_code": "SCH-1001",
        "class_name": "Grade 7",
        "section": "Section B",
        "roll_number": "07-B-11",
        "hostel_wing": "Junior Wing · Rm 112",
        "guardian_name": "Iris Mercer",
        "guardian_relation": "Mother",
        "primary_phone": "+1 (555) 807-4501",
        "secondary_phone": "+1 (555) 807-4502",
        "remaining_minutes": 130,
        "daily_limit_min": 10,
        "wallet_balance": 55.00,
        "validity_start": "2026-08-20",
        "validity_expiry": "2027-05-31",
        "status": "Active"
    },
    {
        "code": "STU-4012",
        "calling_code": "S2D-OAK-8848",
        "name": "Grace Kensington",
        "school_code": "SCH-1001",
        "class_name": "Grade 11",
        "section": "Section B",
        "roll_number": "11-B-26",
        "hostel_wing": "East Gables · Rm 310",
        "guardian_name": "Philip Kensington",
        "guardian_relation": "Father",
        "primary_phone": "+1 (555) 808-9920",
        "secondary_phone": "+1 (555) 808-9921",
        "remaining_minutes": 0,
        "daily_limit_min": 15,
        "wallet_balance": 0.00,
        "validity_start": "2026-08-01",
        "validity_expiry": "2027-05-31",
        "status": "Inactive"
    }
]

FRANCHISES = [
    {
        "code": "FRN-101",
        "name": "North-East EduNet Partners",
        "partner_contact": "Marcus Sterling",
        "email": "m.sterling@northeast-edunet.com",
        "phone": "+1 (555) 340-8800",
        "commission_rate": 18.00,
        "territory": "New England & Mid-Atlantic"
    },
    {
        "code": "FRN-102",
        "name": "Pacific Crest Scholastic Group",
        "partner_contact": "Elena Vasquez",
        "email": "e.vasquez@pacific-crest.org",
        "phone": "+1 (555) 480-1120",
        "commission_rate": 16.00,
        "territory": "West Coast & Pacific Northwest"
    },
    {
        "code": "FRN-103",
        "name": "Heartland Boarding Solutions",
        "partner_contact": "Dwight Campbell",
        "email": "d.campbell@heartland-edu.io",
        "phone": "+1 (555) 790-2340",
        "commission_rate": 15.00,
        "territory": "Midwest & Great Lakes"
    },
    {
        "code": "FRN-104",
        "name": "Atlantic Campus Connect",
        "partner_contact": "Sonia Bhatnagar",
        "email": "s.bhatnagar@atlantic-connect.net",
        "phone": "+1 (555) 610-7790",
        "commission_rate": 15.00,
        "territory": "Southeast & Gulf Coast"
    }
]

INITIAL_SCHOOLS = [
    {
        "code": "SCH-1001",
        "name": "Oakridge Residential Academy",
        "city": "Hartford, CT",
        "franchise_code": "FRN-101",
        "admin_name": "Dr. Arthur Pendelton",
        "admin_email": "admin@oakridge-academy.edu",
        "admin_phone": "+1 (555) 210-9001",
        "student_seats": 684,
        "active_students": 658,
        "enrolled_students": 684,
        "device_count": 28,
        "subscription_plan": "Enterprise Boarding Annual",
        "subscription_status": "Active",
        "status": "Active"
    },
    {
        "code": "SCH-1002",
        "name": "St. Jude Campus & Hostel",
        "city": "Providence, RI",
        "franchise_code": "FRN-101",
        "admin_name": "Sister Theresa Vance",
        "admin_email": "t.vance@stjude-campus.org",
        "admin_phone": "+1 (555) 320-4100",
        "student_seats": 420,
        "active_students": 395,
        "enrolled_students": 412,
        "device_count": 16,
        "subscription_plan": "Campus Growth Annual",
        "subscription_status": "Active",
        "status": "Active"
    },
    {
        "code": "SCH-1003",
        "name": "Pinecrest Boarding Institute",
        "city": "Burlington, VT",
        "franchise_code": "FRN-101",
        "admin_name": "Gregory Ross",
        "admin_email": "g.ross@pinecrest-boarding.edu",
        "admin_phone": "+1 (555) 440-8812",
        "student_seats": 310,
        "active_students": 289,
        "enrolled_students": 305,
        "device_count": 12,
        "subscription_plan": "Campus Growth Annual",
        "subscription_status": "Expiring",
        "status": "Active"
    },
    {
        "code": "SCH-1004",
        "name": "Cascade Crest Preparatory School",
        "city": "Seattle, WA",
        "franchise_code": "FRN-102",
        "admin_name": "Dr. Fiona Zhao",
        "admin_email": "f.zhao@cascadecrest.edu",
        "admin_phone": "+1 (555) 670-3490",
        "student_seats": 850,
        "active_students": 810,
        "enrolled_students": 842,
        "device_count": 34,
        "subscription_plan": "Enterprise Boarding Annual",
        "subscription_status": "Active",
        "status": "Active"
    },
    {
        "code": "SCH-1005",
        "name": "Sierra Foothills Residential Academy",
        "city": "Sacramento, CA",
        "franchise_code": "FRN-102",
        "admin_name": "Marcus Holbrook",
        "admin_email": "m.holbrook@sierrafoothills.org",
        "admin_phone": "+1 (555) 780-9921",
        "student_seats": 520,
        "active_students": 490,
        "enrolled_students": 510,
        "device_count": 22,
        "subscription_plan": "Campus Growth Annual",
        "subscription_status": "Active",
        "status": "Active"
    },
    {
        "code": "SCH-1006",
        "name": "Great Lakes Hostel & Scholastic Campus",
        "city": "Cleveland, OH",
        "franchise_code": "FRN-103",
        "admin_name": "Brenda Kowalski",
        "admin_email": "b.kowalski@greatlakes-hostel.edu",
        "admin_phone": "+1 (555) 910-4433",
        "student_seats": 460,
        "active_students": 440,
        "enrolled_students": 455,
        "device_count": 18,
        "subscription_plan": "Standard Hostel Quarterly",
        "subscription_status": "Active",
        "status": "Active"
    },
    {
        "code": "SCH-1007",
        "name": "Midwest Collegiate Residential School",
        "city": "Indianapolis, IN",
        "franchise_code": "FRN-103",
        "admin_name": "Warren Fletcher",
        "admin_email": "w.fletcher@midwestcollegiate.org",
        "admin_phone": "+1 (555) 830-5511",
        "student_seats": 380,
        "active_students": 0,
        "enrolled_students": 370,
        "device_count": 14,
        "subscription_plan": "Campus Growth Annual",
        "subscription_status": "Expired",
        "status": "Suspended"
    },
    {
        "code": "SCH-1008",
        "name": "Savannah Maritime Boarding Academy",
        "city": "Savannah, GA",
        "franchise_code": "FRN-104",
        "admin_name": "Captain David O'Connor",
        "admin_email": "d.oconnor@savannah-maritime.edu",
        "admin_phone": "+1 (555) 510-6622",
        "student_seats": 590,
        "active_students": 565,
        "enrolled_students": 580,
        "device_count": 24,
        "subscription_plan": "Enterprise Boarding Annual",
        "subscription_status": "Active",
        "status": "Active"
    }
]

class Command(BaseCommand):
    help = "Seed initial franchise and school data, with optional bulk scale benchmark."

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=0, help="Additional bulk schools to generate for scaling tests")

    def handle(self, *args, **options):
        # 1. Seed franchises
        franchise_map = {}
        for f_data in FRANCHISES:
            f, created = Franchise.objects.update_or_create(
                code=f_data["code"],
                defaults=f_data
            )
            franchise_map[f.code] = f
            self.stdout.write(f"{'Created' if created else 'Updated'} franchise: {f.name}")

        # 2. Seed initial realistic schools
        for s_data in INITIAL_SCHOOLS:
            f_code = s_data.pop("franchise_code", None)
            franchise = franchise_map.get(f_code)
            School.objects.update_or_create(
                code=s_data["code"],
                defaults={**s_data, "franchise": franchise, "franchise_name_cache": franchise.name if franchise else ""}
            )
            self.stdout.write(f"Seeded school: {s_data['name']}")

        # 3. Seed realistic students
        for stu_data in INITIAL_STUDENTS:
            sch_code = stu_data.pop("school_code", None)
            school = School.objects.filter(code=sch_code).first()
            if school:
                Student.objects.update_or_create(
                    code=stu_data["code"],
                    defaults={**stu_data, "school": school}
                )
                self.stdout.write(f"Seeded student: {stu_data['name']} ({stu_data['code']}) for {school.name}")

        # Ensure Oakridge and other top schools have a rich roster of students
        oakridge = School.objects.filter(code="SCH-1001").first()
        if oakridge and oakridge.students.count() < 30:
            first_names = ["Oliver", "Emma", "Liam", "Sophia", "Noah", "Ava", "James", "Isabella", "William", "Mia", "Benjamin", "Charlotte", "Elijah", "Amelia", "Lucas", "Harper", "Mason", "Evelyn", "Ethan", "Abigail"]
            last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson"]
            classes = ["Grade 7", "Grade 8", "Grade 9", "Grade 10", "Grade 11", "Grade 12"]
            sections = ["Section A", "Section B", "Section C"]
            wings = ["North Hall · Rm 101", "North Hall · Rm 205", "East Gables · Rm 114", "East Gables · Rm 312", "Junior Wing · Rm 108", "Sports Dormitory Annex"]
            relations = ["Father", "Mother", "Legal Guardian"]

            existing_codes = set(Student.objects.values_list('code', flat=True))
            new_students = []
            for i in range(13, 35):
                code = f"STU-{4000 + i}"
                if code in existing_codes:
                    continue
                calling_code = f"S2D-OAK-{8840 + i}"
                fn = random.choice(first_names)
                ln = random.choice(last_names)
                name = f"{fn} {ln}"
                g_fn = random.choice(first_names)
                g_relation = random.choice(relations)
                g_name = f"{g_fn} {ln}"
                p_phone = f"+1 (555) {random.randint(801, 899):03d}-{random.randint(1000, 9999):04d}"
                s_phone = f"+1 (555) {random.randint(801, 899):03d}-{random.randint(1000, 9999):04d}"
                cls_name = random.choice(classes)
                sec_name = random.choice(sections)
                mins = random.choice([0, 25, 45, 90, 120, 180, 240])
                status = "Active" if mins > 0 else "Inactive"

                new_students.append(Student(
                    code=code,
                    calling_code=calling_code,
                    name=name,
                    gender="Male" if i % 2 == 0 else "Female",
                    school=oakridge,
                    class_name=cls_name,
                    section=sec_name,
                    roll_number=f"{cls_name[-2:]}-{sec_name[-1]}-{i:02d}",
                    hostel_wing=random.choice(wings),
                    guardian_name=g_name,
                    guardian_relation=g_relation,
                    primary_phone=p_phone,
                    secondary_phone=s_phone,
                    remaining_minutes=mins,
                    daily_limit_min=random.choice([10, 15, 20]),
                    wallet_balance=mins * 0.25,
                    validity_start="2026-08-01",
                    validity_expiry="2027-05-31",
                    status=status
                ))
            if new_students:
                Student.objects.bulk_create(new_students)
                self.stdout.write(self.style.SUCCESS(f"Generated {len(new_students)} additional student records for {oakridge.name}."))

        # 3. Optional bulk scale benchmark records
        extra_count = options.get('count', 0)
        if extra_count > 0:
            self.stdout.write(f"Generating {extra_count} bulk schools for high-scale testing...")
            franchises_list = list(Franchise.objects.all())
            cities = ["Chicago, IL", "Dallas, TX", "Austin, TX", "Denver, CO", "Phoenix, AZ", "Miami, FL", "Atlanta, GA", "Boston, MA", "Philadelphia, PA", "Nashville, TN"]
            plans = ["Enterprise Boarding Annual", "Campus Growth Annual", "Standard Hostel Quarterly"]
            statuses = ["Active", "Active", "Active", "Active", "Suspended"]
            sub_statuses = ["Active", "Active", "Active", "Expiring", "Expired"]

            existing_count = School.objects.count()
            bulk_objs = []
            for i in range(1, extra_count + 1):
                num = existing_count + i
                fr = random.choice(franchises_list)
                seats = random.randint(150, 1200)
                active = int(seats * random.uniform(0.85, 0.98))
                status = random.choice(statuses)
                if status == "Suspended":
                    active = 0
                bulk_objs.append(School(
                    code=f"SCH-{num:05d}",
                    name=f"Campus Academy #{num}",
                    city=random.choice(cities),
                    address=f"{random.randint(100, 999)} Academy Boulevard",
                    timezone="America/New_York",
                    franchise=fr,
                    franchise_name_cache=fr.name,
                    admin_name=f"Administrator #{num}",
                    admin_email=f"admin_{num}@s2d-campus.edu",
                    admin_phone=f"+1 (555) {random.randint(200,999):03d}-{random.randint(1000,9999):04d}",
                    daily_duration_cap=random.choice([10, 15, 20, 30]),
                    subscription_plan=random.choice(plans),
                    student_seats=seats,
                    active_students=active,
                    enrolled_students=seats,
                    device_count=random.randint(5, 50),
                    subscription_status=random.choice(sub_statuses),
                    status=status
                ))

            School.objects.bulk_create(bulk_objs, batch_size=2000)
            self.stdout.write(self.style.SUCCESS(f"Successfully generated {extra_count} benchmark schools. Total: {School.objects.count()}"))

