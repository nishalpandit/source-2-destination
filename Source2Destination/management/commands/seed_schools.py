import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from Source2Destination.models import Franchise, School

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
