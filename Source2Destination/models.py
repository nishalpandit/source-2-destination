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
    code = models.CharField(max_length=32, unique=True, db_index=True, help_text="e.g. SCH-101 or HWT-09")
    name = models.CharField(max_length=255, db_index=True, help_text="Official school / hostel name")
    city = models.CharField(max_length=120, db_index=True)
    address = models.TextField(blank=True)
    timezone = models.CharField(max_length=64, default="America/New_York")

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

    # Primary Admin
    admin_name = models.CharField(max_length=255, db_index=True)
    admin_email = models.EmailField(db_index=True)
    admin_phone = models.CharField(max_length=32, blank=True)

    # Calling policies & limits
    daily_duration_cap = models.PositiveIntegerField(default=15, help_text="Daily calling limit in minutes")
    calling_window_start = models.TimeField(default="17:00")
    calling_window_end = models.TimeField(default="19:30")

    # Subscription & Seats
    subscription_plan = models.CharField(
        max_length=100,
        default="Enterprise Boarding Annual",
        db_index=True
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
