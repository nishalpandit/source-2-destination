import uuid
from django.db import models
from django.utils import timezone


class Franchise(models.Model):
    """Regional Franchise Partner managing territories of schools."""
    code = models.CharField(max_length=32, unique=True, db_index=True, help_text="e.g. FRN-101")
    name = models.CharField(max_length=255, db_index=True)
    partner_contact = models.CharField(max_length=255, blank=True)
    email = models.EmailField(db_index=True)
    phone = models.CharField(max_length=32, blank=True)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=18.00, help_text="Percentage e.g. 18.00%")
    territory = models.CharField(max_length=255, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[('Active', 'Active'), ('Suspended', 'Suspended'), ('Pending', 'Pending')],
        default='Active',
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['status', 'name']),
            models.Index(fields=['code', 'status']),
        ]

    def __str__(self):
        return f"{self.code} · {self.name}"


class School(models.Model):
    """
    Campus / Residential School Tenant.
    Engineered with composite indexes and lean query execution to scale to 50k+ records seamlessly.
    """
    # Core Institutional Identity
    code = models.CharField(max_length=32, unique=True, db_index=True, help_text="e.g. SCH-101 or HWT-09")
    name = models.CharField(max_length=255, db_index=True, help_text="Official school / hostel name")
    campus_type = models.CharField(
        max_length=64,
        default="Co-ed Residential Boarding",
        choices=[
            ("Co-ed Residential Boarding", "Co-ed Residential Boarding"),
            ("All-Boys Boarding School", "All-Boys Boarding School"),
            ("All-Girls Boarding School", "All-Girls Boarding School"),
            ("Day-cum-Residential Hostel", "Day-cum-Residential Hostel"),
            ("Military / Preparatory Academy", "Military / Preparatory Academy"),
        ],
        db_index=True
    )
    affiliation_board = models.CharField(
        max_length=64,
        default="CBSE",
        choices=[
            ("CBSE", "CBSE (Central Board)"),
            ("ICSE", "ICSE / ISC"),
            ("IB World", "International Baccalaureate (IB)"),
            ("Cambridge", "Cambridge International (CIE)"),
            ("State Board", "State Board of Education"),
            ("NEASC", "NEASC Accredited"),
        ],
        blank=True
    )
    website = models.URLField(max_length=255, blank=True, help_text="e.g. https://www.hawthorneprep.edu")

    # Location & Physical Campus
    city = models.CharField(max_length=120, db_index=True)
    state = models.CharField(max_length=120, blank=True, default="CT")
    postal_code = models.CharField(max_length=32, blank=True)
    country = models.CharField(max_length=120, default="United States")
    address = models.TextField(blank=True)
    timezone = models.CharField(max_length=64, default="America/New_York")
    hostel_blocks_count = models.PositiveIntegerField(default=4, help_text="Number of active dorm/hostel buildings")

    # Franchise relationship
    franchise = models.ForeignKey(
        Franchise,
        on_delete=models.PROTECT,
        related_name='schools',
        null=True,
        blank=True,
        db_index=True
    )
    franchise_name_cache = models.CharField(max_length=255, blank=True, db_index=True, help_text="Cached for high-speed denormalized queries")

    # Primary Leadership & Contacts
    admin_name = models.CharField(max_length=255, db_index=True, help_text="Principal / Head Administrator Name")
    admin_email = models.EmailField(db_index=True)
    admin_phone = models.CharField(max_length=32, blank=True)
    secondary_contact_name = models.CharField(max_length=255, blank=True, help_text="Campus Hostel Warden / IT In-charge")
    secondary_contact_email = models.EmailField(blank=True)
    secondary_contact_phone = models.CharField(max_length=32, blank=True)

    # Calling policies, Schedules & Limits
    daily_duration_cap = models.PositiveIntegerField(default=15, help_text="Daily calling limit in minutes")
    calling_window_start = models.TimeField(default="17:00")
    calling_window_end = models.TimeField(default="19:30")
    allowed_calling_days = models.CharField(
        max_length=64,
        default="All 7 Days",
        choices=[
            ("All 7 Days", "All 7 Days"),
            ("Weekdays Only (Mon-Fri)", "Weekdays Only (Mon-Fri)"),
            ("Weekends Only (Sat-Sun)", "Weekends Only (Sat-Sun)"),
            ("Mon / Wed / Fri / Sun", "Mon / Wed / Fri / Sun"),
        ]
    )
    emergency_calling_allowed = models.BooleanField(default=True, help_text="Allow emergency outbound calls 24/7")
    kiosk_group_tag = models.CharField(max_length=64, default="AE-HOSTEL-BOOTH", blank=True, help_text="Android Enterprise kiosk device policy tag")

    # Subscription, Billing & Capacity
    subscription_plan = models.CharField(
        max_length=100,
        default="Enterprise Boarding Annual",
        db_index=True
    )
    billing_cycle = models.CharField(
        max_length=32,
        default="Annually",
        choices=[("Annually", "Annually"), ("Quarterly", "Quarterly"), ("Monthly", "Monthly")]
    )
    student_seats = models.PositiveIntegerField(default=550)
    active_students = models.PositiveIntegerField(default=0, db_index=True)
    enrolled_students = models.PositiveIntegerField(default=0)
    device_count = models.PositiveIntegerField(default=0)

    # Account and Subscription Statuses
    subscription_status = models.CharField(
        max_length=20,
        choices=[('Active', 'Active'), ('Expiring', 'Expiring'), ('Expired', 'Expired')],
        default='Active',
        db_index=True
    )
    subscription_expires_at = models.DateField(null=True, blank=True, db_index=True)

    status = models.CharField(
        max_length=20,
        choices=[('Active', 'Active'), ('Suspended', 'Suspended')],
        default='Active',
        db_index=True
    )

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-id']
        indexes = [
            # High-performance composite indexes for 50k+ data querying
            models.Index(fields=['status', 'subscription_status']),
            models.Index(fields=['franchise', 'status']),
            models.Index(fields=['city', 'status']),
            models.Index(fields=['name', 'code']),
            models.Index(fields=['-created_at']),
        ]

    def save(self, *args, **kwargs):
        if self.franchise and not self.franchise_name_cache:
            self.franchise_name_cache = self.franchise.name
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.code} - {self.name} ({self.city})"


class Student(models.Model):
    """
    Enrolled Boarding Student.
    Tied directly to their resident campus, grade, hostel wing, and authorized guardian whitelist.
    """
    code = models.CharField(max_length=32, unique=True, db_index=True, help_text="e.g. STU-4001")
    calling_code = models.CharField(max_length=32, unique=True, db_index=True, help_text="e.g. S2D-OAK-8841")
    name = models.CharField(max_length=255, db_index=True)
    gender = models.CharField(max_length=16, default="Male", choices=[("Male", "Male"), ("Female", "Female"), ("Other", "Other")])
    date_of_birth = models.DateField(null=True, blank=True)

    # Campus & Academic Classification
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='students', db_index=True)
    class_name = models.CharField(max_length=64, db_index=True, help_text="e.g. Grade 10 or Class 12-Science")
    section = models.CharField(max_length=32, default="Section A")
    roll_number = models.CharField(max_length=32, blank=True)
    hostel_wing = models.CharField(max_length=128, blank=True, help_text="e.g. North Hall · Rm 204")

    # Authorized Guardian Contacts (Whitelisted)
    guardian_name = models.CharField(max_length=255, help_text="Primary authorized contact")
    guardian_relation = models.CharField(max_length=64, default="Father", choices=[("Father", "Father"), ("Mother", "Mother"), ("Legal Guardian", "Legal Guardian"), ("Grandparent", "Grandparent")])
    primary_phone = models.CharField(max_length=32, db_index=True, help_text="Whitelisted dialable phone number")
    secondary_phone = models.CharField(max_length=32, blank=True, help_text="Secondary guardian backup number")

    # Calling balance & rules
    remaining_minutes = models.PositiveIntegerField(default=120, help_text="Remaining monthly voice calling minutes")
    daily_limit_min = models.PositiveIntegerField(default=15, help_text="Daily calling duration limit in minutes")
    wallet_balance = models.DecimalField(max_digits=8, decimal_places=2, default=50.00, help_text="Prepaid credit balance ($)")
    validity_start = models.DateField(default=timezone.now)
    validity_expiry = models.DateField(null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=[('Active', 'Active'), ('Inactive', 'Inactive'), ('Suspended', 'Suspended')],
        default='Active',
        db_index=True
    )

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-id']
        indexes = [
            models.Index(fields=['school', 'status']),
            models.Index(fields=['school', 'class_name']),
            models.Index(fields=['code', 'school']),
            models.Index(fields=['primary_phone', 'school']),
        ]

    def __str__(self):
        return f"{self.code} · {self.name} ({self.school.code})"
