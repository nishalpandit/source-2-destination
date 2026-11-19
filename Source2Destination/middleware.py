import re
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth import logout as auth_logout


def is_user_authorized_for_path(user, path):
    """
    Strict portal isolation validator:
    - /super-admin/ -> Super Admin (superuser / admin) ONLY
    - /franchise/   -> Franchise Partner (franchise) ONLY
    - /school-admin/-> School Admin (school / SchoolAdminProfile) ONLY
    Returns True if user is authorized for the given path, False otherwise.
    """
    if not user or not user.is_authenticated:
        return False

    username = user.username.lower() if user.username else ''

    if path.startswith('/super-admin'):
        return bool(user.is_superuser or user.is_staff or username == 'admin')

    if path.startswith('/franchise'):
        # Superuser and School admin are strictly forbidden from Franchise portal
        if user.is_superuser or username == 'school':
            return False
        return bool(username == 'franchise')

    if path.startswith('/school-admin'):
        # Superuser and Franchise admin are strictly forbidden from School Admin portal
        if user.is_superuser or username == 'franchise':
            return False
        if username == 'school':
            return True
        if hasattr(user, 'school_admin_profile'):
            return True
        try:
            from .models import SchoolAdminProfile
            if SchoolAdminProfile.objects.filter(user=user).exists():
                return True
        except Exception:
            pass
        return False

    return True


class RoleAccessMiddleware:
    """
    Unified Institutional Authentication & Role-Based Access Control (RBAC) Middleware.
    Enforces that protected portal routes are guarded by authenticated sessions:
    - Super Admin routes (/super-admin/...) require Superuser / Global HQ privileges.
    - Franchise routes (/franchise/...) require Franchise Partner privileges.
    - School Admin routes (/school-admin/...) require School Administrator privileges.
    
    Strict Isolation Guarantee:
    - Unauthenticated attempts are safely redirected to the single sign-in page.
    - Simply changing the URL in the address bar to another dashboard will NOT allow login.
    - Any attempt to access a dashboard without the matching authenticated credentials
      immediately invalidates/logs out the mismatched session and forces the user to
      authenticate with that dashboard's specific ID and password.
    """

    EXEMPT_PREFIXES = (
        '/static/',
        '/media/',
        '/admin/',
        '/api/',
        '/favicon.ico',
    )

    EXEMPT_EXACT = (
        '/',
        '/login/',
        '/logout/',
        '/auth/login.html',
        '/auth/logout/',
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        # Check exemptions
        if path in self.EXEMPT_EXACT or any(path.startswith(prefix) for prefix in self.EXEMPT_PREFIXES):
            return self.get_response(request)

        # Protect portals: /super-admin/, /franchise/, /school-admin/
        is_super = path.startswith('/super-admin')
        is_franchise = path.startswith('/franchise')
        is_school = path.startswith('/school-admin')

        if is_super or is_franchise or is_school:
            if not request.user.is_authenticated:
                return redirect(f"/?next={path}")

            # Strict portal authentication check:
            # If the user is authenticated but DOES NOT have the credentials for this portal,
            # changing the URL will NOT grant access. Log them out and require ID + password.
            if not is_user_authorized_for_path(request.user, path):
                auth_logout(request)
                return redirect(f"/?next={path}")

        elif not request.user.is_authenticated:
            # Any other protected route outside exemptions requires authentication
            return redirect(f"/?next={path}")

        return self.get_response(request)

