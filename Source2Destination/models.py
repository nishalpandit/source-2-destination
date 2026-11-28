import uuid
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Franchise(models.Model):
    """Regional Franchise Partner managing territories of schools."""
    code = models.CharField(max_length=32, unique=True, db_index=True, help_text="e.g. FRN-101")
    name = models.CharField(max_length=255, db_index=True)
    partner_contact = models.CharField(max_length=255, blank=True)
    email = models.EmailField(db_index=True)
    phone = models.CharField(max_length=32, blank=True)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=18.00, help_text="Percentage e.g. 18.00%")
    territory = models.CharField(max_length=255, blank=True)
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='franchise_partner')
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
    state = models.CharField(max_length=120, blank=True, default="Uttarakhand")
    postal_code = models.CharField(max_length=32, blank=True)
    country = models.CharField(max_length=120, default="India")
    address = models.TextField(blank=True)
    timezone = models.CharField(max_length=64, default="Asia/Kolkata")
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

    # Caller ID Policies, Emergency Overrides & Notification Preferences
    display_school_caller_id = models.BooleanField(default=True, help_text="Display School Name on outbound calls")
    show_guardian_whitelist_numbers = models.BooleanField(default=False, help_text="Show guardian whitelist numbers on kiosk screen")
    emergency_override_caller_id = models.BooleanField(default=True, help_text="Enable emergency override Caller ID")
    primary_emergency_phone = models.CharField(max_length=32, blank=True, default="")
    secondary_emergency_phone = models.CharField(max_length=32, blank=True, default="")
    warden_escalation_phone = models.CharField(max_length=32, blank=True, default="")
    notify_sms_guardians = models.BooleanField(default=True, help_text="Send SMS alerts to guardians")
    notify_email_recharges = models.BooleanField(default=False, help_text="Send email receipts for recharges")
    notify_push_validity = models.BooleanField(default=True, help_text="Send push alerts for validity expiry")

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
    wallet_balance = models.DecimalField(max_digits=8, decimal_places=2, default=50.00, help_text="Prepaid credit balance (₹)")
    validity_start = models.DateField(default=timezone.now)
    validity_expiry = models.DateField(null=True, blank=True)

    # Unique Calling Code Security & Authentication
    pin_policy = models.CharField(max_length=128, default="Unique Code + 4-Digit Student PIN")
    pin = models.CharField(max_length=16, default="1234", blank=True)
    code_status = models.CharField(
        max_length=20,
        default='Active',
        choices=[('Active', 'Active'), ('Suspended', 'Suspended'), ('Pending', 'Pending')],
        db_index=True
    )
    code_issued_at = models.DateTimeField(default=timezone.now)
    code_last_used = models.DateTimeField(null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=[('Active', 'Active'), ('Inactive', 'Inactive'), ('Suspended', 'Suspended')],
        default='Active',
        db_index=True
    )

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def validity_status(self):
        """Dynamic evaluation of student account validity status."""
        if not self.validity_expiry:
            return "Active"
        today = timezone.now().date()
        if today > self.validity_expiry:
            diff_days = (today - self.validity_expiry).days
            if diff_days <= 3:
                return "Grace Period"
            return "Expired"
        elif (self.validity_expiry - today).days <= 14:
            return "Expiring"
        return "Active"

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


class StudentStatusLog(models.Model):
    """
    Audit log for student account lifecycle status transitions.
    Tracks status changes (Active -> Inactive / Suspended) with reasons and authorizing actor.
    """
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='status_logs', db_index=True)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='student_status_logs', db_index=True)
    previous_status = models.CharField(max_length=32)
    new_status = models.CharField(max_length=32, db_index=True)
    reason = models.CharField(max_length=255, default="Administrative update")
    authorized_by = models.CharField(max_length=128, default="School Administrator")
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['school', '-timestamp']),
            models.Index(fields=['student', '-timestamp']),
        ]

    def __str__(self):
        return f"{self.student.name}: {self.previous_status} -> {self.new_status} ({self.timestamp.strftime('%Y-%m-%d %H:%M')})"


class AcademicClass(models.Model):
    """
    Campus Academic Class / Grade level.
    Tied to a specific School campus tenant.
    """
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='academic_classes', db_index=True)
    code = models.CharField(max_length=32, db_index=True, help_text="e.g. CLS-07 or CLS-10")
    name = models.CharField(max_length=64, db_index=True, help_text="e.g. Grade 10 or Class 12")
    supervisor = models.CharField(max_length=255, blank=True, help_text="Grade Coordinator / Faculty Supervisor")
    default_daily_minutes = models.PositiveIntegerField(default=15, help_text="Default daily call limit in minutes")
    schedule_group = models.CharField(max_length=120, default="Standard Hostel Window")
    status = models.CharField(
        max_length=20,
        choices=[('Active', 'Active'), ('Archived', 'Archived')],
        default='Active',
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name', 'id']
        unique_together = ('school', 'name')
        indexes = [
            models.Index(fields=['school', 'status']),
            models.Index(fields=['school', 'name']),
            models.Index(fields=['code', 'school']),
        ]

    def __str__(self):
        return f"{self.name} ({self.school.code})"


class ClassSection(models.Model):
    """
    Academic Section under a Class Grade.
    Includes hostel room/wing mapping, section advisor, and primary calling booth.
    """
    academic_class = models.ForeignKey(AcademicClass, on_delete=models.CASCADE, related_name='sections', db_index=True)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='sections', db_index=True)
    code = models.CharField(max_length=32, db_index=True, help_text="e.g. SEC-10A")
    name = models.CharField(max_length=64, help_text="e.g. Section A")
    room_wing = models.CharField(max_length=128, blank=True, help_text="e.g. North Hall · Floor 2")
    advisor = models.CharField(max_length=255, blank=True, help_text="Section Advisor")
    assigned_booth = models.CharField(max_length=128, default="North Hall Booth 1", help_text="Primary Calling Booth")
    status = models.CharField(
        max_length=20,
        choices=[('Active', 'Active'), ('Archived', 'Archived')],
        default='Active',
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['academic_class', 'name']
        unique_together = ('academic_class', 'name')
        indexes = [
            models.Index(fields=['school', 'status']),
            models.Index(fields=['academic_class', 'status']),
            models.Index(fields=['code', 'school']),
        ]

    def __str__(self):
        return f"{self.academic_class.name} - {self.name} ({self.school.code})"


class Guardian(models.Model):
    """
    Authorized Parent / Legal Guardian Contact for a Student.
    Enforces whitelist authorization on Android Enterprise calling kiosks.
    """
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='guardians', db_index=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='guardian_contacts', db_index=True)
    code = models.CharField(max_length=32, unique=True, db_index=True, help_text="e.g. GRD-501")
    name = models.CharField(max_length=255, db_index=True, help_text="Primary Guardian Full Name")
    relation = models.CharField(
        max_length=64,
        default='Father',
        choices=[
            ('Father', 'Father'),
            ('Mother', 'Mother'),
            ('Legal Guardian', 'Legal Guardian'),
            ('Grandparent', 'Grandparent'),
            ('Other', 'Other')
        ]
    )
    father_phone = models.CharField(max_length=32, blank=True, help_text="Authorized Father Phone")
    mother_phone = models.CharField(max_length=32, blank=True, help_text="Authorized Mother Phone")
    emergency_phone = models.CharField(max_length=32, blank=True, help_text="Secondary/Emergency Phone")
    email = models.EmailField(blank=True)
    verification = models.CharField(max_length=120, default="KYC Verified", help_text="Verification status document")
    whitelist_status = models.CharField(max_length=120, default="Authorized (2 Numbers)")
    status = models.CharField(
        max_length=20,
        choices=[('Active', 'Active'), ('Inactive', 'Inactive')],
        default='Active',
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-id']
        indexes = [
            models.Index(fields=['school', 'status']),
            models.Index(fields=['student', 'status']),
            models.Index(fields=['school', 'name']),
            models.Index(fields=['father_phone', 'school']),
            models.Index(fields=['mother_phone', 'school']),
        ]

    def __str__(self):
        return f"{self.code} · {self.name} ({self.student.name})"


class GlobalDurationRule(models.Model):
    """
    Platform-wide global calling duration governance configured by Super Admin.
    Serves as hard ceilings for all franchises and schools.
    """
    default_call_duration = models.PositiveIntegerField(default=12, help_text="Default per-call duration limit in minutes")
    hard_max_call_duration = models.PositiveIntegerField(default=20, help_text="Hard maximum per-call duration ceiling in minutes")
    max_daily_student_cap = models.PositiveIntegerField(default=30, help_text="Maximum daily cumulative minutes allowed per student")
    max_weekly_student_cap = models.PositiveIntegerField(default=105, help_text="Maximum weekly cumulative minutes allowed per student")
    low_balance_warn_sec = models.PositiveIntegerField(default=60, help_text="Audio warning threshold before auto-disconnect (seconds)")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Global Duration Rule"
        verbose_name_plural = "Global Duration Rules"

    def __str__(self):
        return f"Global Ceiling: Max {self.hard_max_call_duration}m/call · Daily {self.max_daily_student_cap}m"


class CampusDurationRule(models.Model):
    """
    Campus/wing-level duration rules configured by School Admin or Franchise Admin.
    Strictly bounded by GlobalDurationRule hard ceilings.
    """
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='duration_rules', db_index=True)
    scope = models.CharField(max_length=128, default="School-Wide Default", help_text="e.g. School-Wide Default, Junior Wing, Senior Wing")
    academic_class = models.ForeignKey(AcademicClass, on_delete=models.SET_NULL, null=True, blank=True, related_name='duration_rules')
    max_call_duration = models.PositiveIntegerField(default=15, help_text="Per-call limit in minutes (max 20)")
    daily_cumulative_limit = models.PositiveIntegerField(default=15, help_text="Daily cumulative minutes (max 30)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['school', 'scope']
        indexes = [
            models.Index(fields=['school', 'scope']),
        ]

    def __str__(self):
        return f"{self.school.code} · {self.scope}: {self.max_call_duration}m/call"


class CallingScheduleRule(models.Model):
    """
    Time-window calling governance (Baseline Global or School-Specific Override).
    Defines allowed, restricted (curfew/study), or warden-supervised calling windows.
    """
    POLICY_CHOICES = [
        ('allowed', 'Allowed'),
        ('restricted', 'Restricted'),
        ('supervised', 'Supervised'),
    ]

    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True, blank=True, related_name='schedules', db_index=True)
    name = models.CharField(max_length=128, help_text="e.g. Morning Window, Academic Quiet Hours, Evening Calling Window")
    days_of_week = models.CharField(max_length=64, default="MON,TUE,WED,THU,FRI,SAT,SUN", help_text="Comma-separated or day abbreviations")
    start_time = models.TimeField(help_text="Window start e.g. 17:30:00")
    end_time = models.TimeField(help_text="Window end e.g. 21:00:00")
    policy_type = models.CharField(max_length=20, choices=POLICY_CHOICES, default='allowed', db_index=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['start_time']
        indexes = [
            models.Index(fields=['school', 'policy_type']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        scope_str = self.school.code if self.school else "Global Baseline"
        return f"{scope_str} · {self.name} ({self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')}) · {self.policy_type}"


class StudentScheduleException(models.Model):
    """
    Student-wise temporary schedule exception (e.g. for international students whose guardians are abroad).
    """
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='schedule_exceptions', db_index=True)
    allowed_window = models.CharField(max_length=64, help_text="e.g. 06:30 – 07:15")
    valid_until = models.DateField(help_text="Expiration date of timezone exemption")
    reason = models.CharField(max_length=255, default="International timezone guardian calling exemption")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-valid_until']
        indexes = [
            models.Index(fields=['student', 'valid_until']),
        ]

    def __str__(self):
        return f"{self.student.code} · Exception {self.allowed_window} until {self.valid_until}"


class GlobalValidityRule(models.Model):
    """
    Global student calling account validity, expiration, and grace-period policies.
    """
    grace_period_hours = models.PositiveIntegerField(default=72, help_text="Post-expiry grace window in hours")
    reminder_days = models.CharField(max_length=64, default="14,7,3,1", help_text="Comma-separated reminder notification days before expiry")
    preserve_unused_minutes = models.BooleanField(default=True, help_text="Preserve remaining minutes on recharge within 30 days")
    auto_suspend_on_expiry = models.BooleanField(default=True, help_text="Auto-suspend student code on kiosk login when validity expired")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Global Validity Rule"
        verbose_name_plural = "Global Validity Rules"

    def __str__(self):
        return f"Validity Policy: Grace {self.grace_period_hours}h · Auto-Suspend: {self.auto_suspend_on_expiry}"


class RechargePlan(models.Model):
    """
    Standardized student calling recharge pack catalog.
    """
    code = models.CharField(max_length=32, unique=True, db_index=True, help_text="e.g. RPL-01, RPL-02")
    name = models.CharField(max_length=128, db_index=True, help_text="e.g. Standard Term Calling Pack")
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price in INR (₹)")
    minutes_allocated = models.PositiveIntegerField(help_text="Voice minutes credited")
    validity_days = models.PositiveIntegerField(help_text="Validity extension in days")
    per_call_cap = models.PositiveIntegerField(default=15, help_text="Per-call cap override in minutes")
    badge_text = models.CharField(max_length=64, blank=True, help_text="e.g. MOST POPULAR, ANNUAL")
    status = models.CharField(max_length=20, default='Active', choices=[('Active', 'Active'), ('Draft', 'Draft')], db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['price']
        indexes = [
            models.Index(fields=['status', 'price']),
        ]

    def __str__(self):
        return f"{self.code} · {self.name} (₹{self.price} · {self.minutes_allocated}m · {self.validity_days}d)"


class StudentRecharge(models.Model):
    """
    Ledger record for calling credit top-ups and recharge pack activations.
    """
    STATUS_CHOICES = [
        ('Successful', 'Successful'),
        ('Pending', 'Pending'),
        ('Failed', 'Failed'),
    ]

    recharge_id = models.CharField(max_length=64, unique=True, db_index=True, help_text="e.g. RCG-2026-001")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='recharges', db_index=True)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='recharges', db_index=True)
    plan = models.ForeignKey(RechargePlan, on_delete=models.SET_NULL, null=True, blank=True, related_name='recharges')
    plan_name_cache = models.CharField(max_length=128)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    minutes_added = models.PositiveIntegerField()
    validity_days_added = models.PositiveIntegerField()
    payment_mode = models.CharField(max_length=64, default="Campus Bursar Desk Ledger")
    voucher_ref = models.CharField(max_length=128, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Successful', db_index=True)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['school', 'status']),
            models.Index(fields=['student', 'status']),
            models.Index(fields=['created_at', 'status']),
        ]

    def __str__(self):
        return f"{self.recharge_id} · {self.student.name} · {self.plan_name_cache} (₹{self.amount})"


class ValidityExtensionLog(models.Model):
    """
    Audit log of administrative bulk validity extensions.
    """
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='validity_extensions')
    target_type = models.CharField(max_length=64, default="School Cohort")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True)
    days_extended = models.PositiveIntegerField()
    reason = models.CharField(max_length=255)
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-applied_at']

    def __str__(self):
        return f"{self.school.code} extended +{self.days_extended}d ({self.reason})"


class CallRecord(models.Model):
    """
    Campus Voice Call Session & Usage Telemetry Record.
    """
    STATUS_CHOICES = [
        ('Completed', 'Completed'),
        ('Busy', 'Busy'),
        ('No Answer', 'No Answer'),
        ('Restricted Schedule', 'Restricted Schedule'),
        ('Insufficient Credits', 'Insufficient Credits'),
        ('Unauthorized Number', 'Unauthorized Number'),
    ]
    CALL_TYPE_CHOICES = [
        ('Father', 'Father'),
        ('Mother', 'Mother'),
        ('Guardian', 'Guardian'),
        ('Emergency', 'Emergency Contact'),
    ]

    call_id = models.CharField(max_length=64, unique=True, db_index=True, help_text="e.g. CAL-20261114-1001")
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='call_records', db_index=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='call_records', db_index=True)
    guardian = models.ForeignKey(Guardian, on_delete=models.SET_NULL, null=True, blank=True, related_name='calls')
    destination_number = models.CharField(max_length=32, db_index=True)
    call_type = models.CharField(max_length=32, choices=CALL_TYPE_CHOICES, default='Father')
    device_id = models.CharField(max_length=64, default="North Hall Booth 1", help_text="Hostel booth terminal")
    start_time = models.DateTimeField(default=timezone.now, db_index=True)
    end_time = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.PositiveIntegerField(default=0)
    minutes_deducted = models.PositiveIntegerField(default=0)
    call_status = models.CharField(max_length=32, choices=STATUS_CHOICES, default='Completed', db_index=True)
    audio_recording_url = models.CharField(max_length=255, blank=True, default="")

    class Meta:
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['school', 'start_time']),
            models.Index(fields=['student', 'start_time']),
            models.Index(fields=['call_status', 'start_time']),
        ]

    def __str__(self):
        return f"{self.call_id} · {self.student.name} -> {self.destination_number} ({self.duration_seconds}s)"


class KioskDevice(models.Model):
    """
    Hostel Calling Booth & Android Enterprise Dedicated Kiosk Device.
    """
    STATUS_CHOICES = [
        ('Online', 'Online'),
        ('Offline', 'Offline'),
        ('Maintenance', 'Maintenance'),
    ]
    ASSIGNMENT_TYPE_CHOICES = [
        ('Student', 'Dedicated Student Handset (1-to-1)'),
        ('Warden', 'Hostel Warden Handset (1-to-1)'),
    ]

    device_id = models.CharField(max_length=64, unique=True, db_index=True, help_text="e.g. DEV-BOOTH-01")
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='kiosk_devices', db_index=True)
    name = models.CharField(max_length=128, help_text="e.g. North Hall Booth 1")
    serial_number = models.CharField(max_length=64, blank=True, default="")
    mac_address = models.CharField(max_length=64, blank=True, default="")
    imei = models.CharField(max_length=64, blank=True, default="")
    app_version = models.CharField(max_length=32, blank=True, null=True, default="")
    battery_level = models.PositiveIntegerField(default=95, help_text="Percentage battery remaining")
    signal_strength = models.CharField(max_length=32, default="4G LTE (-78 dBm)")
    kiosk_mode_locked = models.BooleanField(default=True, help_text="Android Enterprise lock-task mode")
    hostel_block = models.CharField(max_length=128, default="North Wing")
    assigned_wing = models.CharField(max_length=128, blank=True, default="Junior & Senior Boarding")
    assigned_student = models.ForeignKey(
        'Student',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_devices',
        help_text="Student for 1-to-1 dedicated device binding"
    )
    assigned_warden = models.ForeignKey(
        'HostelWarden',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_devices',
        help_text="Hostel warden for 1-to-1 device binding"
    )
    assignment_type = models.CharField(
        max_length=20,
        choices=ASSIGNMENT_TYPE_CHOICES,
        default='Student',
        help_text="Dedicated 1-to-1 Student Phone vs Hostel Warden Handset"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Online', db_index=True)
    last_heartbeat = models.DateTimeField(default=timezone.now)
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['school', 'status']),
        ]

    def __str__(self):
        if self.assigned_student:
            target = f" -> {self.assigned_student.name}"
        elif self.assigned_warden:
            target = f" -> Warden {self.assigned_warden.name}"
        else:
            target = f" ({self.hostel_block})"
        return f"{self.device_id} · {self.name}{target} [{self.status}]"

    @property
    def is_available(self):
        """Check if device is enrolled, online, and not currently assigned."""
        if self.status != 'Online':
            return False
        if self.assignment_type == 'Student' and self.assigned_student is not None:
            return False
        if self.assignment_type == 'Warden' and self.assigned_warden is not None:
            return False
        return True


class DeviceAssignment(models.Model):
    """
    Mapping between kiosk device and individual students or hostel wardens (1-to-1).
    """
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='device_assignments')
    device = models.ForeignKey(KioskDevice, on_delete=models.CASCADE, related_name='assignments')
    student = models.ForeignKey(
        'Student',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='device_assignments',
        help_text="Assigned student for 1-to-1 device binding"
    )
    warden = models.ForeignKey(
        'HostelWarden',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='device_assignments',
        help_text="Assigned hostel warden for 1-to-1 device binding"
    )
    assignment_type = models.CharField(max_length=20, default='Student', choices=[('Student', 'Student'), ('Warden', 'Hostel Warden')])
    academic_class = models.CharField(max_length=128, blank=True, default="All Classes")
    hostel_wing = models.CharField(max_length=128, default="North Wing")
    assigned_by = models.CharField(max_length=128, default="Campus Administrator")
    assigned_date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=20, default='Active')

    class Meta:
        ordering = ['-assigned_date']

    def __str__(self):
        if self.student:
            return f"{self.device.name} assigned to {self.student.name} ({self.status})"
        if self.warden:
            return f"{self.device.name} assigned to Warden {self.warden.name} ({self.status})"
        return f"{self.device.name} assigned to {self.hostel_wing} ({self.status})"


class HostelWarden(models.Model):
    """
    Hostel Duty Warden & Residential Supervisor.
    """
    STATUS_CHOICES = [
        ('On Duty', 'On Duty'),
        ('Off Duty', 'Off Duty'),
        ('On Leave', 'On Leave'),
    ]

    code = models.CharField(max_length=32, unique=True, db_index=True, help_text="e.g. WRD-101")
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='hostel_wardens', db_index=True)
    name = models.CharField(max_length=128, help_text="e.g. Subedar R.K. Yadav")
    phone = models.CharField(max_length=32)
    email = models.EmailField(blank=True, default="")
    hostel_block = models.CharField(max_length=128, help_text="e.g. North Hall / Shivaji Dorm")
    shift_timings = models.CharField(max_length=64, default="16:00 – 00:00")
    booths_monitored = models.PositiveIntegerField(default=4)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='On Duty', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['school', 'status']),
        ]

    def __str__(self):
        return f"{self.code} · {self.name} ({self.hostel_block})"


class SchoolAdminProfile(models.Model):
    """
    Campus Administrator & Principal Profile.
    Manages school-level portal access, authentication credentials, and hostel oversight.
    """
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Pending Onboarding', 'Pending Onboarding'),
        ('Deactivated', 'Deactivated'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='school_admin_profile', null=True, blank=True)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='admin_profiles', db_index=True)
    admin_id = models.CharField(max_length=32, unique=True, db_index=True, help_text="e.g. ADM-1001")
    name = models.CharField(max_length=128)
    email = models.EmailField(db_index=True)
    phone = models.CharField(max_length=32, blank=True, default="")
    designation = models.CharField(max_length=128, default="Campus Principal / Administrator")
    mfa_enforced = models.BooleanField(default=True)
    is_primary = models.BooleanField(default=False)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default='Active', db_index=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    last_active = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['school', 'status']),
            models.Index(fields=['admin_id', 'status']),
        ]

    def __str__(self):
        return f"{self.admin_id} · {self.name} ({self.school.name})"


class CampusSubscription(models.Model):
    """
    Institutional SaaS Subscription Contract.
    Tracks campus tier, device licensing, student quota, and annual recurring billing.
    """
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Expiring Soon', 'Expiring Soon'),
        ('Expired', 'Expired'),
        ('Past Due', 'Past Due'),
    ]
    TIER_CHOICES = [
        ('Standard Campus', 'Standard Campus'),
        ('Enterprise Boarding', 'Enterprise Boarding'),
        ('Premium Military / Gurukul', 'Premium Military / Gurukul'),
    ]
    BILLING_CHOICES = [
        ('Annual', 'Annual'),
        ('Semi-Annual', 'Semi-Annual'),
        ('Quarterly', 'Quarterly'),
        ('Monthly', 'Monthly'),
    ]

    subscription_id = models.CharField(max_length=64, unique=True, db_index=True, help_text="e.g. SUB-2026-001")
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='subscriptions', db_index=True)
    plan_name = models.CharField(max_length=128, default="Enterprise Residential Tier")
    tier = models.CharField(max_length=64, choices=TIER_CHOICES, default='Enterprise Boarding')
    contract_value = models.DecimalField(max_digits=12, decimal_places=2, default=120000.00)
    billing_cycle = models.CharField(max_length=32, choices=BILLING_CHOICES, default='Annual')
    student_seats = models.PositiveIntegerField(default=500)
    device_seats = models.PositiveIntegerField(default=10)
    start_date = models.DateField(default=timezone.now)
    expiry_date = models.DateField()
    auto_renew = models.BooleanField(default=True)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default='Active', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['school', 'status']),
            models.Index(fields=['status', 'expiry_date']),
        ]

    def __str__(self):
        return f"{self.subscription_id} · {self.school.name} ({self.tier})"


class FinancialTransaction(models.Model):
    """
    Consolidated Institutional & Student Financial Ledger.
    Records all recharges, subscription payments, credit allocations, and settlements.
    """
    STATUS_CHOICES = [
        ('Successful', 'Successful'),
        ('Pending', 'Pending'),
        ('Failed', 'Failed'),
        ('Refunded', 'Refunded'),
    ]
    CATEGORY_CHOICES = [
        ('Student Recharge', 'Student Recharge'),
        ('Annual Subscription', 'Annual Subscription'),
        ('Bulk Credit Allocation', 'Bulk Credit Allocation'),
        ('Subscription Renewal', 'Subscription Renewal'),
        ('Hardware Deposit', 'Hardware Deposit'),
    ]
    PAYMENT_METHOD_CHOICES = [
        ('Razorpay / UPI', 'Razorpay / UPI'),
        ('NEFT / RTGS', 'NEFT / RTGS'),
        ('NetBanking', 'NetBanking'),
        ('Bursar Desk Ledger', 'Bursar Desk Ledger'),
        ('Cash Deposit', 'Cash Deposit'),
    ]

    transaction_id = models.CharField(max_length=64, unique=True, db_index=True, help_text="e.g. TXN-98421")
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='financial_transactions', db_index=True)
    franchise = models.ForeignKey(Franchise, on_delete=models.SET_NULL, null=True, blank=True, related_name='financial_transactions')
    student = models.ForeignKey('Student', on_delete=models.SET_NULL, null=True, blank=True, related_name='financial_transactions')
    category = models.CharField(max_length=64, choices=CATEGORY_CHOICES, default='Student Recharge', db_index=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    payment_method = models.CharField(max_length=64, choices=PAYMENT_METHOD_CHOICES, default='Razorpay / UPI')
    gateway_reference = models.CharField(max_length=128, blank=True, default="")
    payer_name = models.CharField(max_length=128, blank=True, default="")
    invoice_pdf_url = models.CharField(max_length=255, blank=True, default="")
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default='Successful', db_index=True)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['school', 'created_at']),
            models.Index(fields=['category', 'status']),
            models.Index(fields=['status', 'created_at']),
        ]

    def __str__(self):
        return f"{self.transaction_id} · ₹{self.amount} ({self.category} - {self.status})"


class SystemAuditLog(models.Model):
    """
    Immutable System Audit Trail.
    Logs every critical administrative action, policy adjustment, and security event.
    """
    ACTION_CHOICES = [
        ('CREATE', 'CREATE'),
        ('UPDATE', 'UPDATE'),
        ('DELETE', 'DELETE'),
        ('POLICY_OVERRIDE', 'POLICY_OVERRIDE'),
        ('TERMINAL_LOCKDOWN', 'TERMINAL_LOCKDOWN'),
        ('LOGIN', 'LOGIN'),
        ('EXPORT', 'EXPORT'),
    ]

    actor = models.CharField(max_length=128, default="Super Admin")
    actor_role = models.CharField(max_length=64, default="SUPER_ADMIN")
    action_type = models.CharField(max_length=64, choices=ACTION_CHOICES, default='UPDATE', db_index=True)
    target_domain = models.CharField(max_length=64, default="General", db_index=True)
    target_id = models.CharField(max_length=64, blank=True, default="")
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['action_type', 'timestamp']),
            models.Index(fields=['target_domain', 'timestamp']),
        ]

    def __str__(self):
        return f"[{self.timestamp.strftime('%Y-%m-%d %H:%M')}] {self.actor} - {self.action_type} on {self.target_domain}"


class PlatformSetting(models.Model):
    """
    Global Platform Telecommunications & Governance Settings.
    Singleton record storing default parameters, timeouts, and gateway credentials.
    """
    singleton_key = models.CharField(max_length=32, default="default", unique=True)
    platform_title = models.CharField(max_length=128, default="Source2Destination Telecom Control Center")
    support_email = models.EmailField(default="support@source2destination.com")
    support_phone = models.CharField(max_length=32, default="+91 (135) 289-4400")
    emergency_bypass_active = models.BooleanField(default=False)
    session_timeout_minutes = models.PositiveIntegerField(default=30)
    maintenance_mode = models.BooleanField(default=False)
    default_timezone = models.CharField(max_length=64, default="Asia/Kolkata")
    sms_gateway_provider = models.CharField(max_length=32, default="Twilio / Kaleyra")
    sms_api_key = models.CharField(max_length=128, blank=True, default="")
    sms_sender_id = models.CharField(max_length=32, default="S2DEDU")
    low_balance_threshold_minutes = models.PositiveIntegerField(default=15)
    parent_sms_alert_enabled = models.BooleanField(default=True)
    curfew_lockdown_enabled = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Platform Settings ({self.platform_title})"

    @classmethod
    def get_settings(cls):
        obj, _ = cls.objects.get_or_create(singleton_key="default")
        return obj


