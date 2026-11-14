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
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price in USD ($)")
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
        return f"{self.code} · {self.name} (${self.price} · {self.minutes_allocated}m · {self.validity_days}d)"


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
        return f"{self.recharge_id} · {self.student.name} · {self.plan_name_cache} (${self.amount})"


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
    Flowchart: Section 6 'Call History and Usage Database', Section 5 'Call Authorization & Usage Ledger'.
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
    Flowchart: Section 7 'Android Enterprise / Kiosk Device Control', Section 6 'Device and Assignment Database'.
    """
    STATUS_CHOICES = [
        ('Online', 'Online'),
        ('Offline', 'Offline'),
        ('Maintenance', 'Maintenance'),
    ]

    device_id = models.CharField(max_length=64, unique=True, db_index=True, help_text="e.g. DEV-BOOTH-01")
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='kiosk_devices', db_index=True)
    name = models.CharField(max_length=128, help_text="e.g. North Hall Booth 1")
    serial_number = models.CharField(max_length=64, blank=True, default="")
    mac_address = models.CharField(max_length=64, blank=True, default="")
    imei = models.CharField(max_length=64, blank=True, default="")
    app_version = models.CharField(max_length=32, default="v2.4.12-enterprise")
    hostel_block = models.CharField(max_length=128, default="North Wing")
    assigned_wing = models.CharField(max_length=128, blank=True, default="Junior & Senior Boarding")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Online', db_index=True)
    last_heartbeat = models.DateTimeField(default=timezone.now)
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['school', 'status']),
        ]

    def __str__(self):
        return f"{self.device_id} · {self.name} ({self.status})"


class DeviceAssignment(models.Model):
    """
    Mapping between kiosk device, hostel dorms, and student cohorts.
    Flowchart: Section 3 'Assign Device to Student -> Save Device Mapping'.
    """
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='device_assignments')
    device = models.ForeignKey(KioskDevice, on_delete=models.CASCADE, related_name='assignments')
    academic_class = models.CharField(max_length=128, blank=True, default="All Classes")
    hostel_wing = models.CharField(max_length=128, default="North Wing")
    assigned_by = models.CharField(max_length=128, default="Campus Administrator")
    assigned_date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=20, default='Active')

    class Meta:
        ordering = ['-assigned_date']

    def __str__(self):
        return f"{self.device.name} assigned to {self.hostel_wing} ({self.status})"


class HostelWarden(models.Model):
    """
    Hostel Duty Warden & Residential Supervisor.
    Flowchart: Section 6 'Hostel Warden Database', Section 3 'Add / Edit / Assign Hostel Warden'.
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

