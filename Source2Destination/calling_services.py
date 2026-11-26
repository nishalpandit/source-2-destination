"""
Business logic for calling rules, schedules, student validity, and call sessions.
"""
import math
import uuid
from datetime import datetime, time, timedelta
from django.utils import timezone
from django.db import transaction
from django.db.models import Sum, Q
from .models import (
    School, Student, Guardian, GlobalDurationRule, CampusDurationRule,
    CallingScheduleRule, StudentScheduleException, GlobalValidityRule,
    RechargePlan, StudentRecharge, ValidityExtensionLog,
    CallRecord, PlatformSetting, SystemAuditLog
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
    """Calculates per-call and daily duration limits for a student."""
    @classmethod
    def resolve_limits(cls, student):
        global_rule = get_global_duration_rule()

        # start with global limits
        max_call_cap = global_rule.hard_max_call_duration  # 20 mins max
        daily_cap = global_rule.max_daily_student_cap      # 30 mins max

        # check school override
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
    """Checks whether outgoing calls are permitted at the current time."""
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
    """Tracks account validity status, grace periods, and bulk extensions."""
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
    """Handles recharge plans and updates minute balances."""
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
    """Validates student status, validity, whitelist, schedule, and duration."""
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

        # check student account status
        if student.status != 'Active' or student.code_status == 'Suspended':
            return False, 0, "Access denied: Student account is suspended or inactive. Contact school admin."

        # check validity status
        validity = ValidityService.evaluate(student)
        if not validity["is_usable"]:
            return False, 0, "Validity expired: Account calling validity expired. Recharge required."

        # check guardian whitelist
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

        # check calling schedule window
        allowed_in_sched, sched_reason, window_type = CallingScheduleEngine.is_call_allowed(student)
        if not allowed_in_sched:
            return False, 0, f"Time restriction: {sched_reason}"

        # check available duration
        dur_limits = CallingDurationEngine.resolve_limits(student)
        effective_minutes = dur_limits["effective_per_call_limit"]

        if effective_minutes <= 0:
            return False, 0, "Duration limit reached: No calling minutes remaining for today. Recharge required."

        max_seconds = effective_minutes * 60
        return True, max_seconds, f"Authorized: Call granted for up to {effective_minutes} minutes ({window_type})."


class CallSessionManager:
    """Coordinates call session start, end, and minute deductions."""
    @classmethod
    def initiate_session(cls, student_code_or_obj, dialed_number, device_id="Kiosk Booth"):
        """
        Validates calling permissions via CallAuthorizationEngine and provisions a secure session token.
        """
        # Resolve Student
        if isinstance(student_code_or_obj, Student):
            student = student_code_or_obj
        else:
            student = Student.objects.filter(
                Q(code=student_code_or_obj) | Q(calling_code=student_code_or_obj)
            ).select_related('school').first()

        if not student:
            return {
                "authorized": False,
                "reason": "Student authentication failed: Invalid calling code.",
                "session_token": None,
                "max_allowed_seconds": 0
            }

        # Check global platform emergency bypass or curfew lockdown
        platform_settings = PlatformSetting.get_settings()
        if platform_settings.maintenance_mode:
            return {
                "authorized": False,
                "reason": "Campus telecom gateway is currently in scheduled maintenance mode.",
                "session_token": None,
                "max_allowed_seconds": 0
            }

        authorized, max_seconds, reason = CallAuthorizationEngine.authorize_call(student, dialed_number)
        if not authorized:
            return {
                "authorized": False,
                "reason": reason,
                "session_token": None,
                "max_allowed_seconds": 0
            }

        dur_limits = CallingDurationEngine.resolve_limits(student)
        session_token = f"SESS-{uuid.uuid4().hex[:12].upper()}"

        # Resolve guardian recipient name
        recipient_name = "Parent / Guardian"
        clean_dialed = "".join(filter(str.isdigit, str(dialed_number)))
        if student.primary_phone and clean_dialed.endswith("".join(filter(str.isdigit, student.primary_phone))[-10:]):
            recipient_name = student.guardian_name or "Primary Guardian"
        elif student.secondary_phone and clean_dialed.endswith("".join(filter(str.isdigit, student.secondary_phone))[-10:]):
            recipient_name = "Secondary Guardian"
        else:
            for g in student.guardian_contacts.filter(status='Active'):
                if g.father_phone and clean_dialed.endswith("".join(filter(str.isdigit, g.father_phone))[-10:]):
                    recipient_name = f"Father ({g.father_name})" if g.father_name else "Father"
                    break
                if g.mother_phone and clean_dialed.endswith("".join(filter(str.isdigit, g.mother_phone))[-10:]):
                    recipient_name = f"Mother ({g.mother_name})" if g.mother_name else "Mother"
                    break

        return {
            "authorized": True,
            "session_token": session_token,
            "student_id": student.id,
            "student_code": student.code,
            "student_name": student.name,
            "school_id": student.school.id if student.school else None,
            "school_name": student.school.name if student.school else "",
            "recipient_name": recipient_name,
            "dialed_number": dialed_number,
            "device_id": device_id,
            "max_allowed_seconds": max_seconds,
            "low_balance_warn_sec": dur_limits.get("low_balance_warn_sec", 60),
            "remaining_minutes": student.remaining_minutes,
            "reason": reason,
        }

    @classmethod
    def terminate_session(cls, student_code_or_obj, dialed_number, duration_seconds,
                          termination_reason="Completed", device_id="Kiosk Booth",
                          audio_recording_url=""):
        """
        Atomically wraps up a call session:
        - Calculates ceil(duration_seconds / 60)
        - Deducts voice minutes from student's balance
        - Records persistent CallRecord entry
        - Evaluates low-balance notification alert
        """
        if isinstance(student_code_or_obj, Student):
            student = student_code_or_obj
        else:
            student = Student.objects.filter(
                Q(code=student_code_or_obj) | Q(calling_code=student_code_or_obj)
            ).select_related('school').first()

        if not student:
            return {"success": False, "error": "Student not found"}

        minutes_to_deduct = math.ceil(duration_seconds / 60) if duration_seconds > 0 else 0

        with transaction.atomic():
            # Refresh student with lock
            stu = Student.objects.select_for_update().get(pk=student.pk)
            previous_balance = stu.remaining_minutes
            stu.remaining_minutes = max(0, stu.remaining_minutes - minutes_to_deduct)
            stu.save(update_fields=['remaining_minutes'])

            # Determine recipient name
            recipient_name = "Parent / Guardian"
            clean_dialed = "".join(filter(str.isdigit, str(dialed_number)))
            if stu.primary_phone and clean_dialed.endswith("".join(filter(str.isdigit, stu.primary_phone))[-10:]):
                recipient_name = stu.guardian_name or "Primary Guardian"
            elif stu.secondary_phone and clean_dialed.endswith("".join(filter(str.isdigit, stu.secondary_phone))[-10:]):
                recipient_name = "Secondary Guardian"
            else:
                for g in stu.guardian_contacts.filter(status='Active'):
                    if g.father_phone and clean_dialed.endswith("".join(filter(str.isdigit, g.father_phone))[-10:]):
                        recipient_name = f"Father ({g.father_name})" if g.father_name else "Father"
                        break
                    if g.mother_phone and clean_dialed.endswith("".join(filter(str.isdigit, g.mother_phone))[-10:]):
                        recipient_name = f"Mother ({g.mother_name})" if g.mother_name else "Mother"
                        break

            # Map call_type
            call_type = 'Guardian'
            if 'Father' in recipient_name or stu.guardian_relation == 'Father':
                call_type = 'Father'
            elif 'Mother' in recipient_name or stu.guardian_relation == 'Mother':
                call_type = 'Mother'
            elif 'Emergency' in recipient_name:
                call_type = 'Emergency'

            # Create immutable CallRecord
            call_id = f"CAL-{timezone.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:4].upper()}"
            record = CallRecord.objects.create(
                call_id=call_id,
                school=stu.school,
                student=stu,
                destination_number=dialed_number,
                call_type=call_type,
                device_id=device_id,
                start_time=timezone.now() - timedelta(seconds=duration_seconds),
                end_time=timezone.now(),
                duration_seconds=duration_seconds,
                minutes_deducted=minutes_to_deduct,
                call_status=termination_reason,
                audio_recording_url=audio_recording_url
            )

            # Check low balance threshold
            platform_settings = PlatformSetting.get_settings()
            threshold = platform_settings.low_balance_threshold_minutes
            low_balance_triggered = (stu.remaining_minutes <= threshold)

        return {
            "success": True,
            "call_id": record.call_id,
            "student_id": stu.id,
            "student_code": stu.code,
            "minutes_deducted": minutes_to_deduct,
            "previous_balance": previous_balance,
            "remaining_minutes": stu.remaining_minutes,
            "duration_seconds": duration_seconds,
            "call_status": termination_reason,
            "low_balance_alert": low_balance_triggered
        }


