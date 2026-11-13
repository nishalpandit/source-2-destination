import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from Source2Destination.models import (
    Franchise, School, Student, AcademicClass, ClassSection,
    Guardian, StudentStatusLog, RechargePlan, StudentRecharge
)

INITIAL_GUARDIANS = [
    {
        "code": "GRD-501",
        "name": "Rajesh Sharma",
        "student_code": "STU-4001",
        "relation": "Father",
        "father_phone": "+91 98101 23456",
        "mother_phone": "+91 98101 23457",
        "emergency_phone": "+91 98101 23499",
        "email": "rajesh.sharma@example.in",
        "verification": "KYC Verified (Aadhaar)",
        "whitelist_status": "Authorized (2 Numbers)",
        "status": "Active"
    },
    {
        "code": "GRD-502",
        "name": "Meenakshi Iyer",
        "student_code": "STU-4002",
        "relation": "Mother",
        "father_phone": "+91 98450 34568",
        "mother_phone": "+91 98450 34567",
        "emergency_phone": "+91 98450 34500",
        "email": "meenakshi.iyer@example.in",
        "verification": "KYC Verified (Aadhaar)",
        "whitelist_status": "Authorized (2 Numbers)",
        "status": "Active"
    },
    {
        "code": "GRD-503",
        "name": "Sunil Patel",
        "student_code": "STU-4003",
        "relation": "Father",
        "father_phone": "+91 98250 45678",
        "mother_phone": "+91 98250 45679",
        "emergency_phone": "+91 98250 45600",
        "email": "sunil.patel@example.in",
        "verification": "KYC Verified (Aadhaar)",
        "whitelist_status": "Authorized (2 Numbers)",
        "status": "Active"
    },
    {
        "code": "GRD-504",
        "name": "Sunita Sen",
        "student_code": "STU-4004",
        "relation": "Mother",
        "father_phone": "+91 98300 56790",
        "mother_phone": "+91 98300 56789",
        "emergency_phone": "+91 98300 56700",
        "email": "sunita.sen@example.in",
        "verification": "KYC Verified (Aadhaar)",
        "whitelist_status": "Authorized (2 Numbers)",
        "status": "Active"
    },
    {
        "code": "GRD-505",
        "name": "Vikram Verma",
        "student_code": "STU-4005",
        "relation": "Father",
        "father_phone": "+91 98110 67890",
        "mother_phone": "+91 98110 67891",
        "emergency_phone": "+91 98110 67800",
        "email": "vikram.verma@example.in",
        "verification": "Pending Renewal",
        "whitelist_status": "Paused (Account Expired)",
        "status": "Inactive"
    },
    {
        "code": "GRD-506",
        "name": "Ashok Deshmukh",
        "student_code": "STU-4006",
        "relation": "Father",
        "father_phone": "+91 98220 78901",
        "mother_phone": "+91 98220 78902",
        "emergency_phone": "+91 98220 78900",
        "email": "ashok.deshmukh@example.in",
        "verification": "KYC Verified (Aadhaar)",
        "whitelist_status": "Authorized (2 Numbers)",
        "status": "Active"
    }
]

INITIAL_CLASSES = [
    {"code": "CLS-07", "name": "Grade 7", "supervisor": "Smt. Nalini Sharma", "default_daily_minutes": 10, "schedule_group": "Junior Evening Window"},
    {"code": "CLS-08", "name": "Grade 8", "supervisor": "Shri Lokesh Gupta", "default_daily_minutes": 10, "schedule_group": "Junior Evening Window"},
    {"code": "CLS-09", "name": "Grade 9", "supervisor": "Dr. Sunita Rao", "default_daily_minutes": 15, "schedule_group": "Standard Hostel Window"},
    {"code": "CLS-10", "name": "Grade 10", "supervisor": "Prof. Manmohan Verma", "default_daily_minutes": 15, "schedule_group": "Standard Hostel Window"},
    {"code": "CLS-11", "name": "Grade 11", "supervisor": "Dr. Arvind Trivedi", "default_daily_minutes": 15, "schedule_group": "Senior Study-Safe Window"},
    {"code": "CLS-12", "name": "Grade 12", "supervisor": "Prof. Harishankar Pandey", "default_daily_minutes": 20, "schedule_group": "Senior Study-Safe Window"},
]

INITIAL_SECTIONS = [
    {"class_name": "Grade 7", "code": "SEC-07A", "name": "Section A", "room_wing": "Junior Wing · Floor 1", "advisor": "Smt. Nalini Sharma", "assigned_booth": "Junior Wing Kiosk"},
    {"class_name": "Grade 7", "code": "SEC-07B", "name": "Section B", "room_wing": "Junior Wing · Floor 1", "advisor": "Shri Deepak Mishra", "assigned_booth": "Junior Wing Kiosk"},
    {"class_name": "Grade 7", "code": "SEC-07C", "name": "Section C", "room_wing": "Junior Wing · Floor 2", "advisor": "Smt. Priyanka Rawat", "assigned_booth": "Junior Wing Kiosk"},
    {"class_name": "Grade 8", "code": "SEC-08A", "name": "Section A", "room_wing": "Junior Wing · Floor 1", "advisor": "Shri Lokesh Gupta", "assigned_booth": "Junior Wing Kiosk"},
    {"class_name": "Grade 8", "code": "SEC-08B", "name": "Section B", "room_wing": "Junior Wing · Floor 2", "advisor": "Smt. Archana Joshi", "assigned_booth": "Junior Wing Kiosk"},
    {"class_name": "Grade 8", "code": "SEC-08C", "name": "Section C", "room_wing": "Junior Wing · Floor 2", "advisor": "Shri Santosh Negi", "assigned_booth": "Junior Wing Kiosk"},
    {"class_name": "Grade 9", "code": "SEC-09A", "name": "Section A", "room_wing": "Sarojini Sadan · Floor 1", "advisor": "Shri Alok Saxena", "assigned_booth": "Sarojini Sadan Booth 1"},
    {"class_name": "Grade 9", "code": "SEC-09B", "name": "Section B", "room_wing": "Sarojini Sadan · Floor 1", "advisor": "Dr. Sunita Rao", "assigned_booth": "Sarojini Sadan Booth 1"},
    {"class_name": "Grade 9", "code": "SEC-09C", "name": "Section C", "room_wing": "Sarojini Sadan · Floor 2", "advisor": "Smt. Geeta Goswami", "assigned_booth": "Sarojini Sadan Booth 1"},
    {"class_name": "Grade 10", "code": "SEC-10A", "name": "Section A", "room_wing": "Tagore Bhavan · Floor 2", "advisor": "Prof. Manmohan Verma", "assigned_booth": "Tagore Bhavan Booth 1"},
    {"class_name": "Grade 10", "code": "SEC-10B", "name": "Section B", "room_wing": "Sarojini Sadan · Floor 2", "advisor": "Smt. Kavita Pillai", "assigned_booth": "Sarojini Sadan Booth 1"},
    {"class_name": "Grade 10", "code": "SEC-10C", "name": "Section C", "room_wing": "Tagore Bhavan · Floor 2", "advisor": "Dr. Ramesh Nair", "assigned_booth": "Tagore Bhavan Booth 2"},
    {"class_name": "Grade 11", "code": "SEC-11A", "name": "Section A", "room_wing": "Tagore Bhavan · Floor 3", "advisor": "Dr. Arvind Trivedi", "assigned_booth": "Tagore Bhavan Booth 2"},
    {"class_name": "Grade 11", "code": "SEC-11B", "name": "Section B", "room_wing": "Tagore Bhavan · Floor 3", "advisor": "Shri Gopal Kulkarni", "assigned_booth": "Tagore Bhavan Booth 2"},
    {"class_name": "Grade 11", "code": "SEC-11C", "name": "Section C", "room_wing": "Sarojini Sadan · Floor 3", "advisor": "Smt. Manjula Sen", "assigned_booth": "Sarojini Sadan Booth 2"},
    {"class_name": "Grade 12", "code": "SEC-12A", "name": "Section A", "room_wing": "Tagore Bhavan · Floor 4", "advisor": "Prof. Harishankar Pandey", "assigned_booth": "Tagore Bhavan Booth 2"},
    {"class_name": "Grade 12", "code": "SEC-12B", "name": "Section B", "room_wing": "Tagore Bhavan · Floor 4", "advisor": "Dr. Tarun Bhattacharya", "assigned_booth": "Tagore Bhavan Booth 2"},
    {"class_name": "Grade 12", "code": "SEC-12C", "name": "Section C", "room_wing": "Sarojini Sadan · Floor 3", "advisor": "Smt. Vandana Shukla", "assigned_booth": "Sarojini Sadan Booth 2"},
]

INITIAL_STUDENTS = [
    {
        "code": "STU-4001",
        "calling_code": "S2D-DOON-8801",
        "name": "Aarav Sharma",
        "gender": "Male",
        "school_code": "SCH-1001",
        "class_name": "Grade 10",
        "section": "Section A",
        "roll_number": "10-A-14",
        "hostel_wing": "Tagore Bhavan · Rm 204",
        "guardian_name": "Rajesh Sharma",
        "guardian_relation": "Father",
        "primary_phone": "+91 98101 23456",
        "secondary_phone": "+91 98101 23457",
        "remaining_minutes": 180,
        "daily_limit_min": 15,
        "wallet_balance": 499.00,
        "validity_start": "2026-08-01",
        "validity_expiry": "2027-05-31",
        "status": "Active"
    },
    {
        "code": "STU-4002",
        "calling_code": "S2D-DOON-8802",
        "name": "Ananya Iyer",
        "gender": "Female",
        "school_code": "SCH-1001",
        "class_name": "Grade 9",
        "section": "Section B",
        "roll_number": "09-B-08",
        "hostel_wing": "Sarojini Sadan · Rm 112",
        "guardian_name": "Meenakshi Iyer",
        "guardian_relation": "Mother",
        "primary_phone": "+91 98450 34567",
        "secondary_phone": "+91 98450 34568",
        "remaining_minutes": 120,
        "daily_limit_min": 15,
        "wallet_balance": 199.00,
        "validity_start": "2026-08-01",
        "validity_expiry": "2027-05-31",
        "status": "Active"
    },
    {
        "code": "STU-4003",
        "calling_code": "S2D-DOON-8803",
        "name": "Vihaan Patel",
        "gender": "Male",
        "school_code": "SCH-1001",
        "class_name": "Grade 11",
        "section": "Section A",
        "roll_number": "11-A-03",
        "hostel_wing": "Tagore Bhavan · Rm 308",
        "guardian_name": "Sunil Patel",
        "guardian_relation": "Father",
        "primary_phone": "+91 98250 45678",
        "secondary_phone": "+91 98250 45679",
        "remaining_minutes": 24,
        "daily_limit_min": 12,
        "wallet_balance": 49.00,
        "validity_start": "2026-05-15",
        "validity_expiry": "2026-11-20",
        "status": "Active"
    },
    {
        "code": "STU-4004",
        "calling_code": "S2D-DOON-8804",
        "name": "Diya Sen",
        "gender": "Female",
        "school_code": "SCH-1001",
        "class_name": "Grade 12",
        "section": "Section C",
        "roll_number": "12-C-19",
        "hostel_wing": "Sarojini Sadan · Rm 305",
        "guardian_name": "Sunita Sen",
        "guardian_relation": "Mother",
        "primary_phone": "+91 98300 56789",
        "secondary_phone": "+91 98300 56790",
        "remaining_minutes": 215,
        "daily_limit_min": 20,
        "wallet_balance": 1499.00,
        "validity_start": "2026-08-10",
        "validity_expiry": "2027-06-15",
        "status": "Active"
    },
    {
        "code": "STU-4005",
        "calling_code": "S2D-DOON-8805",
        "name": "Aditya Verma",
        "gender": "Male",
        "school_code": "SCH-1001",
        "class_name": "Grade 8",
        "section": "Section A",
        "roll_number": "08-A-03",
        "hostel_wing": "Junior Wing · Rm 105",
        "guardian_name": "Vikram Verma",
        "guardian_relation": "Father",
        "primary_phone": "+91 98110 67890",
        "secondary_phone": "+91 98110 67891",
        "remaining_minutes": 0,
        "daily_limit_min": 10,
        "wallet_balance": 0.00,
        "validity_start": "2026-04-01",
        "validity_expiry": "2026-10-31",
        "status": "Inactive"
    },
    {
        "code": "STU-4006",
        "calling_code": "S2D-DOON-8806",
        "name": "Tanvi Deshmukh",
        "gender": "Female",
        "school_code": "SCH-1001",
        "class_name": "Grade 10",
        "section": "Section B",
        "roll_number": "10-B-19",
        "hostel_wing": "Sarojini Sadan · Rm 214",
        "guardian_name": "Ashok Deshmukh",
        "guardian_relation": "Father",
        "primary_phone": "+91 98220 78901",
        "secondary_phone": "+91 98220 78902",
        "remaining_minutes": 75,
        "daily_limit_min": 15,
        "wallet_balance": 199.00,
        "validity_start": "2026-06-01",
        "validity_expiry": "2026-11-22",
        "status": "Active"
    },
    {
        "code": "STU-4007",
        "calling_code": "S2D-DOON-8807",
        "name": "Rohan Gupta",
        "gender": "Male",
        "school_code": "SCH-1001",
        "class_name": "Grade 11",
        "section": "Section A",
        "roll_number": "11-A-09",
        "hostel_wing": "Tagore Bhavan · Rm 102",
        "guardian_name": "Manoj Gupta",
        "guardian_relation": "Father",
        "primary_phone": "+91 98105 89012",
        "secondary_phone": "+91 98105 89013",
        "remaining_minutes": 190,
        "daily_limit_min": 15,
        "wallet_balance": 499.00,
        "validity_start": "2026-08-15",
        "validity_expiry": "2027-05-30",
        "status": "Active"
    },
    {
        "code": "STU-4008",
        "calling_code": "S2D-DOON-8808",
        "name": "Kavya Reddy",
        "gender": "Female",
        "school_code": "SCH-1001",
        "class_name": "Grade 9",
        "section": "Section C",
        "roll_number": "09-C-15",
        "hostel_wing": "Sarojini Sadan · Rm 118",
        "guardian_name": "Suresh Reddy",
        "guardian_relation": "Father",
        "primary_phone": "+91 98490 90123",
        "secondary_phone": "+91 98490 90124",
        "remaining_minutes": 110,
        "daily_limit_min": 15,
        "wallet_balance": 199.00,
        "validity_start": "2026-08-15",
        "validity_expiry": "2027-05-30",
        "status": "Active"
    },
    {
        "code": "STU-4009",
        "calling_code": "S2D-DOON-8809",
        "name": "Ishaan Sharma",
        "gender": "Male",
        "school_code": "SCH-1001",
        "class_name": "Grade 12",
        "section": "Section A",
        "roll_number": "12-A-04",
        "hostel_wing": "Tagore Bhavan · Rm 401",
        "guardian_name": "Pooja Sharma",
        "guardian_relation": "Mother",
        "primary_phone": "+91 98112 01234",
        "secondary_phone": "+91 98112 01235",
        "remaining_minutes": 30,
        "daily_limit_min": 15,
        "wallet_balance": 99.00,
        "validity_start": "2026-05-20",
        "validity_expiry": "2026-11-20",
        "status": "Active"
    },
    {
        "code": "STU-4010",
        "calling_code": "S2D-DOON-8810",
        "name": "Priya Nair",
        "gender": "Female",
        "school_code": "SCH-1001",
        "class_name": "Grade 10",
        "section": "Section A",
        "roll_number": "10-A-17",
        "hostel_wing": "Sarojini Sadan · Rm 220",
        "guardian_name": "Radha Nair",
        "guardian_relation": "Mother",
        "primary_phone": "+91 98471 12345",
        "secondary_phone": "+91 98471 12346",
        "remaining_minutes": 240,
        "daily_limit_min": 20,
        "wallet_balance": 1499.00,
        "validity_start": "2026-09-01",
        "validity_expiry": "2027-06-30",
        "status": "Active"
    },
    {
        "code": "STU-4011",
        "calling_code": "S2D-DOON-8811",
        "name": "Aryan Joshi",
        "gender": "Male",
        "school_code": "SCH-1001",
        "class_name": "Grade 7",
        "section": "Section B",
        "roll_number": "07-B-11",
        "hostel_wing": "Junior Wing · Rm 112",
        "guardian_name": "Deepak Joshi",
        "guardian_relation": "Father",
        "primary_phone": "+91 98260 23456",
        "secondary_phone": "+91 98260 23457",
        "remaining_minutes": 130,
        "daily_limit_min": 10,
        "wallet_balance": 199.00,
        "validity_start": "2026-08-20",
        "validity_expiry": "2027-05-31",
        "status": "Active"
    },
    {
        "code": "STU-4012",
        "calling_code": "S2D-DOON-8812",
        "name": "Saanvi Kulkarni",
        "gender": "Female",
        "school_code": "SCH-1001",
        "class_name": "Grade 11",
        "section": "Section B",
        "roll_number": "11-B-26",
        "hostel_wing": "Sarojini Sadan · Rm 310",
        "guardian_name": "Mahesh Kulkarni",
        "guardian_relation": "Father",
        "primary_phone": "+91 98230 34567",
        "secondary_phone": "+91 98230 34568",
        "remaining_minutes": 160,
        "daily_limit_min": 15,
        "wallet_balance": 499.00,
        "validity_start": "2026-08-01",
        "validity_expiry": "2027-05-31",
        "status": "Active"
    },
    {
        "code": "STU-4013",
        "calling_code": "S2D-DOON-8813",
        "name": "Kabir Malhotra",
        "gender": "Male",
        "school_code": "SCH-1001",
        "class_name": "Grade 8",
        "section": "Section C",
        "roll_number": "08-C-15",
        "hostel_wing": "Junior Wing · Rm 115",
        "guardian_name": "Amit Malhotra",
        "guardian_relation": "Father",
        "primary_phone": "+91 98103 45678",
        "secondary_phone": "+91 98103 45679",
        "remaining_minutes": 85,
        "daily_limit_min": 10,
        "wallet_balance": 199.00,
        "validity_start": "2026-08-01",
        "validity_expiry": "2027-05-31",
        "status": "Active"
    },
    {
        "code": "STU-4014",
        "calling_code": "S2D-DOON-8814",
        "name": "Anika Choudhury",
        "gender": "Female",
        "school_code": "SCH-1001",
        "class_name": "Grade 10",
        "section": "Section C",
        "roll_number": "10-C-05",
        "hostel_wing": "Sarojini Sadan · Rm 222",
        "guardian_name": "Bikram Choudhury",
        "guardian_relation": "Father",
        "primary_phone": "+91 98310 56789",
        "secondary_phone": "+91 98310 56790",
        "remaining_minutes": 200,
        "daily_limit_min": 15,
        "wallet_balance": 499.00,
        "validity_start": "2026-08-01",
        "validity_expiry": "2027-05-31",
        "status": "Active"
    },
    {
        "code": "STU-4015",
        "calling_code": "S2D-DOON-8815",
        "name": "Dhruv Singhal",
        "gender": "Male",
        "school_code": "SCH-1001",
        "class_name": "Grade 12",
        "section": "Section B",
        "roll_number": "12-B-12",
        "hostel_wing": "Tagore Bhavan · Rm 405",
        "guardian_name": "Alok Singhal",
        "guardian_relation": "Father",
        "primary_phone": "+91 98107 67890",
        "secondary_phone": "+91 98107 67891",
        "remaining_minutes": 140,
        "daily_limit_min": 20,
        "wallet_balance": 499.00,
        "validity_start": "2026-08-01",
        "validity_expiry": "2027-05-31",
        "status": "Active"
    }
]

FRANCHISES = [
    {
        "code": "FRN-101",
        "name": "North India EduNet Partners",
        "partner_contact": "Vikramaditya Singhania",
        "email": "v.singhania@northedunet.in",
        "phone": "+91 98111 22334",
        "commission_rate": 18.00,
        "territory": "North India Boarding Corridor (Uttarakhand, HP, Punjab)"
    },
    {
        "code": "FRN-102",
        "name": "Western Scholastic Network",
        "partner_contact": "Sunita Deshmukh",
        "email": "s.deshmukh@westernscholastic.in",
        "phone": "+91 98220 33445",
        "commission_rate": 16.00,
        "territory": "Western Region (Maharashtra & Gujarat)"
    },
    {
        "code": "FRN-103",
        "name": "Central Heartland Edutech",
        "partner_contact": "Rajeshwar Bundela",
        "email": "r.bundela@heartlandedutech.in",
        "phone": "+91 98260 44556",
        "commission_rate": 15.00,
        "territory": "Central Region (Madhya Pradesh & Rajasthan)"
    },
    {
        "code": "FRN-104",
        "name": "Southern Campus Connect",
        "partner_contact": "K. R. Meenakshi",
        "email": "kr.meenakshi@southerncampus.in",
        "phone": "+91 98450 55667",
        "commission_rate": 15.00,
        "territory": "South India Network (Karnataka & Tamil Nadu)"
    }
]

INITIAL_SCHOOLS = [
    {
        "code": "SCH-1001",
        "name": "Doon Valley Residential Academy",
        "city": "Dehradun, Uttarakhand",
        "franchise_code": "FRN-101",
        "admin_name": "Dr. Ramesh Chandra Sharma",
        "admin_email": "principal@doonvalley.edu.in",
        "admin_phone": "+91 98101 23456",
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
        "name": "Mayo International Boarding School",
        "city": "Ajmer, Rajasthan",
        "franchise_code": "FRN-103",
        "admin_name": "Col. Devendra Rathore",
        "admin_email": "admin@mayointernational.edu.in",
        "admin_phone": "+91 98290 34567",
        "student_seats": 512,
        "active_students": 494,
        "enrolled_students": 505,
        "device_count": 22,
        "subscription_plan": "Campus Growth Annual",
        "subscription_status": "Active",
        "status": "Active"
    },
    {
        "code": "SCH-1003",
        "name": "Scindia Residential Campus",
        "city": "Gwalior, Madhya Pradesh",
        "franchise_code": "FRN-103",
        "admin_name": "Dr. Aniruddh Madhavrao",
        "admin_email": "rector@scindiacampus.edu.in",
        "admin_phone": "+91 98260 56789",
        "student_seats": 430,
        "active_students": 405,
        "enrolled_students": 420,
        "device_count": 18,
        "subscription_plan": "Campus Growth Annual",
        "subscription_status": "Expiring",
        "status": "Active"
    },
    {
        "code": "SCH-1004",
        "name": "Bishop Cotton Boys School & Hostel",
        "city": "Shimla, Himachal Pradesh",
        "franchise_code": "FRN-101",
        "admin_name": "Rev. Joydeep Mukherjee",
        "admin_email": "headmaster@bishopcottonshimla.edu.in",
        "admin_phone": "+91 98160 67890",
        "student_seats": 790,
        "active_students": 771,
        "enrolled_students": 785,
        "device_count": 34,
        "subscription_plan": "Enterprise Boarding Annual",
        "subscription_status": "Active",
        "status": "Active"
    },
    {
        "code": "SCH-1005",
        "name": "Sahyadri International Residential School",
        "city": "Pune, Maharashtra",
        "franchise_code": "FRN-102",
        "admin_name": "Dr. Sanjay Kulkarni",
        "admin_email": "s.kulkarni@sahyadriresidential.edu.in",
        "admin_phone": "+91 98230 78901",
        "student_seats": 345,
        "active_students": 318,
        "enrolled_students": 335,
        "device_count": 14,
        "subscription_plan": "Standard Hostel Quarterly",
        "subscription_status": "Active",
        "status": "Active"
    }
]

INITIAL_RECHARGE_PLANS = [
    {
        "code": "RPL-01",
        "name": "Starter Monthly Pack",
        "price": 199.00,
        "minutes_allocated": 100,
        "validity_days": 30,
        "per_call_cap": 10,
        "badge_text": "",
        "status": "Active"
    },
    {
        "code": "RPL-02",
        "name": "Standard Term Calling Pack",
        "price": 499.00,
        "minutes_allocated": 300,
        "validity_days": 90,
        "per_call_cap": 15,
        "badge_text": "Popular",
        "status": "Active"
    },
    {
        "code": "RPL-03",
        "name": "Full Academic Year Pack",
        "price": 1499.00,
        "minutes_allocated": 1000,
        "validity_days": 365,
        "per_call_cap": 15,
        "badge_text": "Best Value",
        "status": "Active"
    },
    {
        "code": "RPL-04",
        "name": "Emergency Top-Up Booster",
        "price": 99.00,
        "minutes_allocated": 45,
        "validity_days": 14,
        "per_call_cap": 10,
        "badge_text": "Booster",
        "status": "Active"
    }
]

class Command(BaseCommand):
    help = "Seed realistic Indian franchises, schools, students, classes, and recharge plans."

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=0, help="Additional bulk schools to generate")

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
            s_copy = dict(s_data)
            f_code = s_copy.pop("franchise_code", None)
            franchise = franchise_map.get(f_code)
            School.objects.update_or_create(
                code=s_copy["code"],
                defaults={**s_copy, "franchise": franchise, "franchise_name_cache": franchise.name if franchise else ""}
            )
            self.stdout.write(f"Seeded school: {s_data['name']}")

        primary_school = School.objects.filter(code="SCH-1001").first()

        # 3. Seed realistic Indian students
        for stu_data in INITIAL_STUDENTS:
            stu_copy = dict(stu_data)
            sch_code = stu_copy.pop("school_code", None)
            school = School.objects.filter(code=sch_code).first() or primary_school
            if school:
                Student.objects.update_or_create(
                    code=stu_copy["code"],
                    defaults={**stu_copy, "school": school}
                )
                self.stdout.write(f"Seeded student: {stu_data['name']} ({stu_data['code']}) for {school.name}")

        # 4. Seed Classes and Sections
        if primary_school:
            class_map = {}
            for c_data in INITIAL_CLASSES:
                c_obj, created = AcademicClass.objects.update_or_create(
                    school=primary_school,
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
                            "school": primary_school,
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
            g_copy = dict(g_data)
            stu_code = g_copy.pop("student_code", None)
            student = Student.objects.filter(code=stu_code).first()
            if student:
                g_obj, created = Guardian.objects.update_or_create(
                    code=g_copy["code"],
                    defaults={
                        **g_copy,
                        "student": student,
                        "school": student.school
                    }
                )
                self.stdout.write(f"{'Created' if created else 'Updated'} guardian: {g_obj.name} for {student.name}")

        # Ensure all students of primary school have guardians
        if primary_school:
            idx = 510
            for stu in primary_school.students.all():
                if not Guardian.objects.filter(student=stu).exists():
                    f_phone = stu.primary_phone if stu.guardian_relation == 'Father' else ''
                    m_phone = stu.primary_phone if stu.guardian_relation == 'Mother' else ''
                    Guardian.objects.create(
                        school=primary_school,
                        student=stu,
                        code=f"GRD-{idx}",
                        name=stu.guardian_name,
                        relation=stu.guardian_relation,
                        father_phone=f_phone or "+91 98101 23456",
                        mother_phone=m_phone or "+91 98101 23457",
                        emergency_phone=stu.secondary_phone or "+91 98101 23499",
                        email=f"{stu.guardian_name.lower().replace(' ', '.')}@example.in",
                        verification="KYC Verified (Aadhaar)",
                        whitelist_status="Authorized (2 Numbers)",
                        status=stu.status
                    )
                    idx += 1

        # 6. Seed Indian Recharge Plans (₹)
        for p_data in INITIAL_RECHARGE_PLANS:
            plan, created = RechargePlan.objects.update_or_create(
                code=p_data["code"],
                defaults=p_data
            )
            self.stdout.write(f"{'Created' if created else 'Updated'} plan: {plan.name} (₹{plan.price})")

        # 7. Seed Student Recharge transactions if empty
        if primary_school and not StudentRecharge.objects.filter(school=primary_school).exists():
            plan_term = RechargePlan.objects.filter(code="RPL-02").first()
            plan_annual = RechargePlan.objects.filter(code="RPL-03").first()
            stus = list(primary_school.students.all()[:4])
            if stus and plan_term:
                StudentRecharge.objects.create(
                    student=stus[0],
                    school=primary_school,
                    plan=plan_term,
                    amount=plan_term.price,
                    minutes_added=plan_term.minutes_allocated,
                    validity_days_added=plan_term.validity_days,
                    payment_mode="UPI / Razorpay",
                    gateway_ref="PAY-RZP-994821A",
                    status="Completed",
                    plan_name_cache=plan_term.name,
                    notes="Authorized guardian term pack topup"
                )
            if len(stus) > 1 and plan_annual:
                StudentRecharge.objects.create(
                    student=stus[1],
                    school=primary_school,
                    plan=plan_annual,
                    amount=plan_annual.price,
                    minutes_added=plan_annual.minutes_allocated,
                    validity_days_added=plan_annual.validity_days,
                    payment_mode="UPI / PhonePe",
                    gateway_ref="PAY-RZP-994822B",
                    status="Completed",
                    plan_name_cache=plan_annual.name,
                    notes="Annual academic year topup"
                )
            self.stdout.write(self.style.SUCCESS("Seeded initial Indian StudentRecharge records."))

        # 8. Seed Status Logs if empty
        if not StudentStatusLog.objects.exists() and primary_school:
            stu_active = Student.objects.filter(code='STU-4001').first()
            stu_inactive = Student.objects.filter(code='STU-4005').first()
            if stu_inactive:
                StudentStatusLog.objects.create(
                    student=stu_inactive,
                    school=primary_school,
                    previous_status="Active",
                    new_status="Inactive",
                    reason="Term validity expired",
                    authorized_by="Policy Engine"
                )
            if stu_active:
                StudentStatusLog.objects.create(
                    student=stu_active,
                    school=primary_school,
                    previous_status="Inactive",
                    new_status="Active",
                    reason="Account renewed via ₹499 pack",
                    authorized_by="Dr. Ramesh Chandra Sharma"
                )
            self.stdout.write(self.style.SUCCESS("Seeded initial StudentStatusLog transition audit history."))

        self.stdout.write(self.style.SUCCESS("Successfully seeded authentic Indian educational platform data!"))
