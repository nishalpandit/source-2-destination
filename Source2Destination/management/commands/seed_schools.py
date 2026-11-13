import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from Source2Destination.models import Franchise, School, Student, AcademicClass, ClassSection, Guardian, StudentStatusLog

INITIAL_GUARDIANS = [
    {
        "code": "GRD-501",
        "name": "Robert Hawthorne",
        "student_code": "STU-4001",
        "relation": "Father",
        "father_phone": "+1 (555) 801-2210",
        "mother_phone": "+1 (555) 801-2211",
        "emergency_phone": "+1 (555) 801-2299",
        "email": "r.hawthorne@example.com",
        "verification": "KYC Verified",
        "whitelist_status": "Authorized (2 Numbers)",
        "status": "Active"
    },
    {
        "code": "GRD-502",
        "name": "Margaret Bennett",
        "student_code": "STU-4002",
        "relation": "Mother",
        "father_phone": "+1 (555) 802-3499",
        "mother_phone": "+1 (555) 802-3490",
        "emergency_phone": "+1 (555) 802-3400",
        "email": "m.bennett@example.com",
        "verification": "KYC Verified",
        "whitelist_status": "Authorized (2 Numbers)",
        "status": "Active"
    },
    {
        "code": "GRD-503",
        "name": "David Montgomery",
        "student_code": "STU-4003",
        "relation": "Father",
        "father_phone": "+1 (555) 803-5120",
        "mother_phone": "+1 (555) 803-5125",
        "emergency_phone": "+1 (555) 803-5199",
        "email": "d.montgomery@example.com",
        "verification": "KYC Verified",
        "whitelist_status": "Authorized (2 Numbers)",
        "status": "Active"
    },
    {
        "code": "GRD-504",
        "name": "Evelyn Fletcher",
        "student_code": "STU-4004",
        "relation": "Mother",
        "father_phone": "+1 (555) 804-7741",
        "mother_phone": "+1 (555) 804-7740",
        "emergency_phone": "+1 (555) 804-7700",
        "email": "e.fletcher@example.com",
        "verification": "KYC Verified",
        "whitelist_status": "Authorized (3 Numbers)",
        "status": "Active"
    },
    {
        "code": "GRD-505",
        "name": "Henry Kingsley",
        "student_code": "STU-4005",
        "relation": "Father",
        "father_phone": "+1 (555) 805-1192",
        "mother_phone": "+1 (555) 805-1198",
        "emergency_phone": "+1 (555) 805-1100",
        "email": "h.kingsley@example.com",
        "verification": "Pending Renewal",
        "whitelist_status": "Paused (Account Expired)",
        "status": "Inactive"
    },
    {
        "code": "GRD-506",
        "name": "Catherine Whitaker",
        "student_code": "STU-4006",
        "relation": "Legal Guardian",
        "father_phone": "",
        "mother_phone": "",
        "emergency_phone": "+1 (555) 806-6631",
        "email": "c.whitaker@example.com",
        "verification": "Court Letter Verified",
        "whitelist_status": "Authorized (1 Number)",
        "status": "Active"
    }
]

INITIAL_CLASSES = [
    {"code": "CLS-07", "name": "Grade 7", "supervisor": "Mrs. Nadine Wallace", "default_daily_minutes": 10, "schedule_group": "Junior Evening Window"},
    {"code": "CLS-08", "name": "Grade 8", "supervisor": "Mr. Leonard Grant", "default_daily_minutes": 10, "schedule_group": "Junior Evening Window"},
    {"code": "CLS-09", "name": "Grade 9", "supervisor": "Ms. Rachel Donovan", "default_daily_minutes": 15, "schedule_group": "Standard Hostel Window"},
    {"code": "CLS-10", "name": "Grade 10", "supervisor": "Mr. Victor Sterling", "default_daily_minutes": 15, "schedule_group": "Standard Hostel Window"},
    {"code": "CLS-11", "name": "Grade 11", "supervisor": "Dr. Helena Price", "default_daily_minutes": 15, "schedule_group": "Senior Study-Safe Window"},
    {"code": "CLS-12", "name": "Grade 12", "supervisor": "Prof. Malcolm Reed", "default_daily_minutes": 20, "schedule_group": "Senior Study-Safe Window"},
]

INITIAL_SECTIONS = [
    {"class_name": "Grade 7", "code": "SEC-07A", "name": "Section A", "room_wing": "Junior Wing · Floor 1", "advisor": "Mrs. Nadine Wallace", "assigned_booth": "Junior Wing Kiosk"},
    {"class_name": "Grade 7", "code": "SEC-07B", "name": "Section B", "room_wing": "Junior Wing · Floor 1", "advisor": "Mr. Kenneth Moore", "assigned_booth": "Junior Wing Kiosk"},
    {"class_name": "Grade 7", "code": "SEC-07C", "name": "Section C", "room_wing": "Junior Wing · Floor 2", "advisor": "Ms. Chloe Adams", "assigned_booth": "Junior Wing Kiosk"},
    {"class_name": "Grade 8", "code": "SEC-08A", "name": "Section A", "room_wing": "Junior Wing · Floor 1", "advisor": "Mr. Leonard Grant", "assigned_booth": "Junior Wing Kiosk"},
    {"class_name": "Grade 8", "code": "SEC-08B", "name": "Section B", "room_wing": "Junior Wing · Floor 2", "advisor": "Mrs. Abigail Evans", "assigned_booth": "Junior Wing Kiosk"},
    {"class_name": "Grade 8", "code": "SEC-08C", "name": "Section C", "room_wing": "Junior Wing · Floor 2", "advisor": "Mr. Dennis Cole", "assigned_booth": "Junior Wing Kiosk"},
    {"class_name": "Grade 9", "code": "SEC-09A", "name": "Section A", "room_wing": "East Gables · Floor 1", "advisor": "Mr. Ian Wright", "assigned_booth": "East Gables Booth 1"},
    {"class_name": "Grade 9", "code": "SEC-09B", "name": "Section B", "room_wing": "East Gables · Floor 1", "advisor": "Ms. Rachel Donovan", "assigned_booth": "East Gables Booth 1"},
    {"class_name": "Grade 9", "code": "SEC-09C", "name": "Section C", "room_wing": "East Gables · Floor 2", "advisor": "Mrs. Patricia Hall", "assigned_booth": "East Gables Booth 1"},
    {"class_name": "Grade 10", "code": "SEC-10A", "name": "Section A", "room_wing": "North Hall · Floor 2", "advisor": "Mr. Victor Sterling", "assigned_booth": "North Hall Booth 1"},
    {"class_name": "Grade 10", "code": "SEC-10B", "name": "Section B", "room_wing": "East Gables · Floor 2", "advisor": "Ms. Claire Sutton", "assigned_booth": "East Gables Booth 1"},
    {"class_name": "Grade 10", "code": "SEC-10C", "name": "Section C", "room_wing": "North Hall · Floor 2", "advisor": "Dr. Alan Foster", "assigned_booth": "North Hall Booth 2"},
    {"class_name": "Grade 11", "code": "SEC-11A", "name": "Section A", "room_wing": "North Hall · Floor 3", "advisor": "Dr. Helena Price", "assigned_booth": "North Hall Booth 2"},
    {"class_name": "Grade 11", "code": "SEC-11B", "name": "Section B", "room_wing": "North Hall · Floor 3", "advisor": "Mr. Gregory Palmer", "assigned_booth": "North Hall Booth 2"},
    {"class_name": "Grade 11", "code": "SEC-11C", "name": "Section C", "room_wing": "East Gables · Floor 3", "advisor": "Ms. Valerie King", "assigned_booth": "East Gables Booth 2"},
    {"class_name": "Grade 12", "code": "SEC-12A", "name": "Section A", "room_wing": "North Hall · Floor 4", "advisor": "Prof. Malcolm Reed", "assigned_booth": "North Hall Booth 2"},
    {"class_name": "Grade 12", "code": "SEC-12B", "name": "Section B", "room_wing": "North Hall · Floor 4", "advisor": "Dr. Timothy Vance", "assigned_booth": "North Hall Booth 2"},
    {"class_name": "Grade 12", "code": "SEC-12C", "name": "Section C", "room_wing": "East Gables · Floor 3", "advisor": "Prof. Malcolm Reed", "assigned_booth": "East Gables Booth 2"},
]

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

        # 4. Seed Classes and Sections for Schools (starting with Oakridge)
        if oakridge:
            class_map = {}
            for c_data in INITIAL_CLASSES:
                c_obj, created = AcademicClass.objects.update_or_create(
                    school=oakridge,
                    name=c_data["name"],
                    defaults={
                        "code": c_data["code"],
                        "supervisor": c_data["supervisor"],
                        "default_daily_minutes": c_data["default_daily_minutes"],
                        "schedule_group": c_data["schedule_group"],
                        "status": "Active"
                    }
                )
                class_map[c_obj.name] = c_obj
                self.stdout.write(f"{'Created' if created else 'Updated'} class: {c_obj.name}")

            for s_data in INITIAL_SECTIONS:
                parent_class = class_map.get(s_data["class_name"])
                if parent_class:
                    sec_obj, created = ClassSection.objects.update_or_create(
                        academic_class=parent_class,
                        name=s_data["name"],
                        defaults={
                            "school": oakridge,
                            "code": s_data["code"],
                            "room_wing": s_data["room_wing"],
                            "advisor": s_data["advisor"],
                            "assigned_booth": s_data["assigned_booth"],
                            "status": "Active"
                        }
                    )
                    self.stdout.write(f"{'Created' if created else 'Updated'} section: {parent_class.name} - {sec_obj.name}")

        # 5. Seed Guardians for Students
        for g_data in INITIAL_GUARDIANS:
            stu_code = g_data.pop("student_code", None)
            student = Student.objects.filter(code=stu_code).first()
            if student:
                g_obj, created = Guardian.objects.update_or_create(
                    code=g_data["code"],
                    defaults={
                        **g_data,
                        "student": student,
                        "school": student.school
                    }
                )
                self.stdout.write(f"{'Created' if created else 'Updated'} guardian: {g_obj.name} for {student.name}")

        # Ensure all students of Oakridge have at least one authorized guardian
        if oakridge:
            students_without_guardians = oakridge.students.filter(guardian_contacts__isnull=True)
            new_guardians = []
            idx = 507
            for stu in students_without_guardians:
                g_code = f"GRD-{idx}"
                idx += 1
                f_phone = stu.primary_phone if stu.guardian_relation == 'Father' else ''
                m_phone = stu.primary_phone if stu.guardian_relation == 'Mother' else ''
                new_guardians.append(Guardian(
                    school=oakridge,
                    student=stu,
                    code=g_code,
                    name=stu.guardian_name,
                    relation=stu.guardian_relation,
                    father_phone=f_phone or f"+1 (555) {random.randint(801, 899):03d}-{random.randint(1000, 9999):04d}",
                    mother_phone=m_phone or (stu.secondary_phone if stu.secondary_phone else f"+1 (555) {random.randint(801, 899):03d}-{random.randint(1000, 9999):04d}"),
                    emergency_phone=stu.secondary_phone or "",
                    email=f"{stu.guardian_name.lower().replace(' ', '.')}@example.com",
                    verification="KYC Verified",
                    whitelist_status="Authorized (2 Numbers)",
                    status=stu.status
                ))
            if new_guardians:
                Guardian.objects.bulk_create(new_guardians)
                self.stdout.write(self.style.SUCCESS(f"Generated {len(new_guardians)} additional guardian records for {oakridge.name}."))

        # 6. Seed Status Logs if empty
        if not StudentStatusLog.objects.exists() and oakridge:
            stu_liam = Student.objects.filter(code='STU-4001').first()
            stu_oliver = Student.objects.filter(code='STU-4005').first()
            if stu_oliver:
                StudentStatusLog.objects.create(
                    student=stu_oliver,
                    school=oakridge,
                    previous_status="Active",
                    new_status="Inactive",
                    reason="Term validity expired",
                    authorized_by="Policy Worker"
                )
            if stu_liam:
                StudentStatusLog.objects.create(
                    student=stu_liam,
                    school=oakridge,
                    previous_status="Inactive",
                    new_status="Active",
                    reason="Returned from medical leave",
                    authorized_by="Dr. Arthur Pendelton"
                )
            self.stdout.write(self.style.SUCCESS("Seeded initial StudentStatusLog transition audit history."))

        # 6. Optional bulk scale benchmark records
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

