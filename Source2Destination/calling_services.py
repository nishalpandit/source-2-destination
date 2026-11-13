"""
Calling Rules, Schedules, Validity & Credit Engines
Source 2 Destination — Shared Business Logic (Flowchart Layer 5)
Provides precision engines for:
1. Calling Duration Rules & Ceilings
2. Weekly Calling Schedules & Curfew Quiet Hours
3. Student Validity & Expiration Lifecycle
4. Recharge Plans, Credit Ledger & Top-ups
5. Call Authorization Engine (whitelisting, schedules, duration, validity)
"""
from datetime import datetime, time, timedelta
from django.utils import timezone
from django.db import transaction
from django.db.models import Sum, Q
from .models import (
    School, Student, Guardian, GlobalDurationRule, CampusDurationRule,
    CallingScheduleRule, StudentScheduleException, GlobalValidityRule,
    RechargePlan, StudentRecharge, ValidityExtensionLog
)


def get_global_duration_rule():
    """Retrieve or initialize default global duration ceilings."""
    rule = GlobalDurationRule.objects.first()
    if not rule:
        rule = GlobalDurationRule.objects.create(
            default_call_duration=12,
            hard_max_call_duration=20,
            max_daily_student_cap=30,
            max_weekly_student_cap=105,
            low_balance_warn_sec=60
        )
    return rule


def get_global_validity_rule():
    """Retrieve or initialize default global validity policy."""
    rule = GlobalValidityRule.objects.first()
    if not rule:
        rule = GlobalValidityRule.objects.create(
            grace_period_hours=72,
            reminder_days="14,7,3,1",
            preserve_unused_minutes=True,
            auto_suspend_on_expiry=True
        )
    return rule


class CallingDurationEngine:
    """
    Computes effective per-call and daily calling duration limits for a student,
    strictly bounded by Super Admin hard ceilings and Franchise/School policies.
    """
    @classmethod
    def resolve_limits(cls, student):
        global_rule = get_global_duration_rule()

        # Baseline limits from Super Admin ceiling
        max_call_cap = global_rule.hard_max_call_duration  # 20 mins max
        daily_cap = global_rule.max_daily_student_cap      # 30 mins max

        # Check campus-specific duration rule (if defined)
        if student and student.school:
            campus_rule = CampusDurationRule.objects.filter(
                school=student.school,
                scope="School-Wide Default"
            ).first()

            if campus_rule:
                max_call_cap = min(max_call_cap, campus_rule.max_call_duration)
                daily_cap = min(daily_cap, campus_rule.daily_cumulative_limit)

            # Check wing / class override
            if "Junior" in student.class_name or any(g in student.class_name for g in ["7", "8"]):
                junior_rule = CampusDurationRule.objects.filter(
                    school=student.school,
                    scope="Junior Wing (Grades 7–8)"
                ).first()
                if junior_rule:
                    max_call_cap = min(max_call_cap, junior_rule.max_call_duration)
                    daily_cap = min(daily_cap, junior_rule.daily_cumulative_limit)

            # Check school level duration cap
            if student.school.daily_duration_cap:
                daily_cap = min(daily_cap, student.school.daily_duration_cap)

        # Also bound by individual student assigned daily limit
        if student and student.daily_limit_min:
            daily_cap = min(daily_cap, student.daily_limit_min)

        # Available voice minutes cannot exceed student balance
        available_minutes = student.remaining_minutes if student else 0
        effective_call_max = min(max_call_cap, daily_cap, available_minutes)

        return {
            "hard_max_call_duration": global_rule.hard_max_call_duration,
            "max_daily_student_cap": global_rule.max_daily_student_cap,
            "low_balance_warn_sec": global_rule.low_balance_warn_sec,
            "effective_per_call_limit": max(0, effective_call_max),
            "effective_daily_cap": daily_cap,
            "remaining_minutes": available_minutes,
        }


class CallingScheduleEngine:
    """
    Evaluates whether an outgoing call request is within authorized schedule windows,
    respecting academic quiet hours, curfew cutoffs, and student-wise exceptions.
    """
    DAY_ABBREVIATIONS = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]

    @classmethod
    def is_call_allowed(cls, student, check_dt=None):
        """
        Check if student can place a call right now.
        Returns (is_allowed: bool, reason: str, window_type: str)
        """
        if check_dt is None:
            check_dt = timezone.localtime()

        current_day = cls.DAY_ABBREVIATIONS[check_dt.weekday()]
        current_time = check_dt.time()

        # Check 1: Student-wise international timezone exception
        if student:
            exception = StudentScheduleException.objects.filter(
                student=student,
                valid_until__gte=check_dt.date()
            ).first()
            if exception:
                # e.g. "06:30 – 07:15"
                try:
                    parts = exception.allowed_window.replace(' ', '').split('–')
                    if len(parts) == 1:
                        parts = exception.allowed_window.replace(' ', '').split('-')
                    if len(parts) == 2:
                        s_h, s_m = map(int, parts[0].split(':'))
                        e_h, e_m = map(int, parts[1].split(':'))
                        if time(s_h, s_m) <= current_time <= time(e_h, e_m):
                            return True, "Call permitted under active international timezone exception.", "exception"
                except Exception:
                    pass

        # Check 2: School-specific or Global Baseline schedules
        school = student.school if student else None
        schedules = CallingScheduleRule.objects.filter(
            Q(school=school) | Q(school__isnull=True),
            is_active=True
        ).order_by('school__id', 'start_time')

        if not schedules.exists():
            # Default window: allow 17:00 - 21:00, curfew outside
            if time(17, 0) <= current_time <= time(21, 0):
                return True, "Within regular evening hostel calling hours.", "allowed"
            return False, "Calling disallowed outside evening hostel window (17:00 – 21:00).", "restricted"

        # Check matching schedule rules for current day
        for sched in schedules:
            days = [d.strip().upper() for d in sched.days_of_week.split(',')]
            if current_day in days or "ALL" in days or ("MON-FRI" in sched.days_of_week and current_day in ["MON", "TUE", "WED", "THU", "FRI"]):
                if sched.start_time <= current_time <= sched.end_time:
                    if sched.policy_type == 'allowed':
                        return True, f"Permitted window: {sched.name}.", "allowed"
                    elif sched.policy_type == 'supervised':
                        return True, f"Warden-supervised window: {sched.name}.", "supervised"
                    else:
                        return False, f"Restricted academic curfew: {sched.name}.", "restricted"

        # If outside all explicit allowed windows:
        return False, "Current time is outside authorized campus calling slots.", "restricted"


class ValidityService:
    """
    Manages account validity lifecycle, reminders, grace periods, and bulk extensions.
    """
    @classmethod
    def evaluate(cls, student):
        """
        Returns full status dossier:
        { 'status': 'Active'|'Expiring'|'Grace Period'|'Expired', 'days_left': int, 'is_usable': bool }
        """
        if not student.validity_expiry:
            return {"status": "Active", "days_left": 999, "is_usable": True}

        today = timezone.now().date()
        diff = (student.validity_expiry - today).days

        if diff >= 14:
            return {"status": "Active", "days_left": diff, "is_usable": True}
        elif 0 <= diff < 14:
            return {"status": "Expiring", "days_left": diff, "is_usable": True}
        elif -3 <= diff < 0:
            return {"status": "Grace Period", "days_left": diff, "is_usable": True}
        else:
            return {"status": "Expired", "days_left": diff, "is_usable": False}

    @classmethod
    def bulk_extend(cls, school, days, reason, target_cohort="School Cohort"):
        """Extend validity for school students and record audit log."""
        students = Student.objects.filter(school=school) if school else Student.objects.all()
        today = timezone.now().date()
        updated_count = 0

        with transaction.atomic():
            for stu in students:
                base_date = stu.validity_expiry if (stu.validity_expiry and stu.validity_expiry >= today) else today
                stu.validity_expiry = base_date + timedelta(days=days)
                if stu.status == 'Suspended':
                    stu.status = 'Active'
                if stu.code_status == 'Suspended':
                    stu.code_status = 'Active'
                stu.save(update_fields=['validity_expiry', 'status', 'code_status'])
                updated_count += 1

            if school:
                ValidityExtensionLog.objects.create(
                    school=school,
                    target_type=target_cohort,
                    days_extended=days,
                    reason=reason
                )

        return updated_count


class RechargeService:
    """
    Handles calling pack activations, minute balance top-ups, and ledger recordings.
    """
    @classmethod
    def process_recharge(cls, student, plan, payment_mode="Campus Bursar Desk Ledger", voucher_ref="", status="Successful"):
        """
        Activates a recharge plan for a student:
        - Adds minutes to remaining_minutes
        - Extends validity_expiry by plan.validity_days
        - Updates student status to Active
        - Records StudentRecharge ledger entry
        """
        today = timezone.now().date()

        with transaction.atomic():
            # Calculate new validity expiry
            base_date = student.validity_expiry if (student.validity_expiry and student.validity_expiry >= today) else today
            new_expiry = base_date + timedelta(days=plan.validity_days)

            student.remaining_minutes += plan.minutes_allocated
            student.validity_expiry = new_expiry
            student.status = 'Active'
            student.code_status = 'Active'
            student.save(update_fields=['remaining_minutes', 'validity_expiry', 'status', 'code_status'])

            recharge_id = f"RCG-{student.school.code[:3] if student.school else 'S2D'}-{timezone.now().strftime('%Y%m%d')}-{StudentRecharge.objects.count() + 101}"

            recharge = StudentRecharge.objects.create(
                recharge_id=recharge_id,
                student=student,
                school=student.school,
                plan=plan,
                plan_name_cache=plan.name,
                amount=plan.price,
                minutes_added=plan.minutes_allocated,
                validity_days_added=plan.validity_days,
                payment_mode=payment_mode,
                voucher_ref=voucher_ref or recharge_id,
                status=status
            )

        return recharge


class CallAuthorizationEngine:
    """
    Precision Call Authorization Engine matching Layer 5 of flowchart:
    All Calling Conditions Passed?
    1. Check Enrolled Student Account Status (Active?)
    2. Calling Validity Active? (Not Expired?)
    3. Within Authorized Schedule?
    4. Dialed Number Authorized on Guardian Whitelist?
    5. Available Duration Remaining?
    -> Return (authorized: bool, max_seconds: int, reason: str)
    """
    @classmethod
    def authorize_call(cls, student_code_or_obj, dialed_number):
        # Resolve Student
        if isinstance(student_code_or_obj, Student):
            student = student_code_or_obj
        else:
            student = Student.objects.filter(
                Q(code=student_code_or_obj) | Q(calling_code=student_code_or_obj)
            ).select_related('school').first()

        if not student:
            return False, 0, "Student authentication failed: Invalid calling code."

        # Check 1: Account Status
        if student.status != 'Active' or student.code_status == 'Suspended':
            return False, 0, "Access denied: Student account is suspended or inactive. Contact school admin."

        # Check 2: Validity Status
        validity = ValidityService.evaluate(student)
        if not validity["is_usable"]:
            return False, 0, "Validity expired: Account calling validity expired. Recharge required."

        # Check 3: Authorized Guardian Whitelist
        clean_dialed = "".join(filter(str.isdigit, str(dialed_number)))
        authorized_numbers = []

        if student.primary_phone:
            authorized_numbers.append("".join(filter(str.isdigit, student.primary_phone)))
        if student.secondary_phone:
            authorized_numbers.append("".join(filter(str.isdigit, student.secondary_phone)))

        # Also check Guardian contacts whitelist
        for g in student.guardian_contacts.filter(status='Active'):
            if g.father_phone:
                authorized_numbers.append("".join(filter(str.isdigit, g.father_phone)))
            if g.mother_phone:
                authorized_numbers.append("".join(filter(str.isdigit, g.mother_phone)))
            if g.emergency_phone:
                authorized_numbers.append("".join(filter(str.isdigit, g.emergency_phone)))

        # Match (allow last 10 digits comparison)
        is_whitelisted = False
        for auth_num in authorized_numbers:
            if auth_num and (clean_dialed == auth_num or clean_dialed.endswith(auth_num[-10:]) or auth_num.endswith(clean_dialed[-10:])):
                is_whitelisted = True
                break

        if not is_whitelisted:
            return False, 0, f"Unauthorized number: Dialing {dialed_number} is rejected by parent whitelist policy."

        # Check 4: Within Authorized Schedule Window
        allowed_in_sched, sched_reason, window_type = CallingScheduleEngine.is_call_allowed(student)
        if not allowed_in_sched:
            return False, 0, f"Time restriction: {sched_reason}"

        # Check 5: Available Duration
        dur_limits = CallingDurationEngine.resolve_limits(student)
        effective_minutes = dur_limits["effective_per_call_limit"]

        if effective_minutes <= 0:
            return False, 0, "Duration limit reached: No calling minutes remaining for today. Recharge required."

        max_seconds = effective_minutes * 60
        return True, max_seconds, f"Authorized: Call granted for up to {effective_minutes} minutes ({window_type})."
